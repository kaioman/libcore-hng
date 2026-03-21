import os
import time
import jwt
import requests
import google.oauth2.credentials
from pathlib import Path
from typing import Union, Optional, Dict, Any
from google.cloud import secretmanager
from cryptography.fernet import Fernet, InvalidToken
from libcore_hng.exceptions import CryptoException
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import base64
from libcore_hng.configs.gcp import GcpConfig

def _generate_subject_token(
    private_key_path: str, 
    issuer: str, 
    project_number: str, 
    pool_id: str, 
    provider_id: str,
    kid: str) -> str:
    """
    秘密鍵で署名した自前JWTを生成する

    Parameters
    ----------
    private_key_path : str
        秘密鍵ファイルのパス
    issuer : str
        JWTの発行者
    project_number : str
        GCPプロジェクト番号
    pool_id : str
        Workload Identity Pool ID
    provider_id : str
        Workload Identity Provider ID
    kid : str
        JWTヘッダーのKey ID(KID)

    Returns
    -------
    str
        生成されたJWT
    """
    
    now = int(time.time())
    with open(private_key_path, "rb") as f:
        private_key_pem = f.read()

    payload = {
        "iss": issuer,
        "sub": "libcore-hng-wif-user", 
        "aud": f"https://iam.googleapis.com/projects/{project_number}/locations/global/workloadIdentityPools/{pool_id}/providers/{provider_id}",
        "iat": now,
        "exp": now + 3600, # 有効期限1時間
    }

    headers = {"kid": kid}
    return jwt.encode(payload, private_key_pem, algorithm="RS256", headers=headers)

def _get_secret_with_wif(
    secret_id: str, 
    project_number: str, 
    pool_id: str, provider_id: str, 
    service_account_email: str, 
    issuer: str, 
    private_key_path: str, 
    sts_url: str,
    sts_grant_type: str,
    sts_requested_token_type: str,
    sts_scope: str,
    sts_subject_token_type: str,
    iam_credentials_url_base: str,
    kid: str) -> Optional[bytes]:
    """
    Workload Identity Federation を使用して Secret Manager からシークレットを取得する

    Parameters
    ----------
    secret_id : str
        取得するシークレットのID
    project_number : str
        GCPプロジェクト番号
    pool_id : str
        Workload Identity Pool ID
    provider_id : str
        Workload Identity Provider ID
    service_account_email : str
        なりすますサービスアカウントのメールアドレス
    issuer : str
        JWTの発行者
    private_key_path : str
        秘密鍵ファイルのパス
    kid : str
        JWTヘッダーのKey ID(KID)

    Returns
    -------
    Optional[bytes]
        取得したシークレットのバイト列。見つからない場合はNone

    Raises
    ------
    CryptoException
        Workload Identity Federation経由でのSecret Managerからの鍵取得に失敗した場合
    """
    try:
        # 1. 自前JWT（Subject Token）を作成
        subject_token = _generate_subject_token(private_key_path, issuer, project_number, pool_id, provider_id, kid)

        # 2. Google STS エンドポイントに投げて、Googleの一時トークンに交換
        data = {
            "audience": f"//iam.googleapis.com/projects/{project_number}/locations/global/workloadIdentityPools/{pool_id}/providers/{provider_id}",
            "grantType": sts_grant_type,
            "requestedTokenType": sts_requested_token_type,
            "scope": sts_scope,
            "subjectToken": subject_token,
            "subjectTokenType": sts_subject_token_type,
        }
        
        response = requests.post(sts_url, data=data)
        response.raise_for_status()
        federated_token = response.json()["access_token"]

        # 3. サービスアカウントになりすます (Impersonation)
        iam_url = f"{iam_credentials_url_base}/v1/projects/-/serviceAccounts/{service_account_email}:generateAccessToken"
        headers = {"Authorization": f"Bearer {federated_token}"}
        payload = {"scope": [sts_scope]}
        
        response = requests.post(iam_url, headers=headers, json=payload)
        response.raise_for_status()
        final_access_token = response.json()["accessToken"]

        # 4. 最終的なトークンを使って Secret Manager から値を取得
        client = secretmanager.SecretManagerServiceClient(
            credentials=google.oauth2.credentials.Credentials(final_access_token)
        )
        name = f"projects/{project_number}/secrets/{secret_id}/versions/latest"
        response = client.access_secret_version(request={"name": name})
        return response.payload.data
    except Exception as e:
        raise CryptoException(f"Workload Identity Federation経由でのSecret Managerからの鍵取得に失敗しました: {e}")

def _get_gcp_secret_key(gcp_config: GcpConfig) -> Optional[bytes]:
    """
    GCP Secret Managerから復号鍵を取得する。Workload Identity Federationが設定されている場合はそちらを優先する。

    Returns
    -------
    Optional[bytes]
        GCP Secret Managerから取得した復号鍵。設定がない場合はNone。

    Raises
    ------
    CryptoException
        GCP Secret Managerからの鍵取得に失敗した場合
    """
    if gcp_config.wif_enabled:
        # Workload Identity Federation が有効な場合
        project_number = gcp_config.project_number
        pool_id = gcp_config.pool_id
        provider_id = gcp_config.provider_id
        service_account_email = gcp_config.service_account_email
        issuer = gcp_config.issuer
        kid = gcp_config.kid
        sts_url = gcp_config.sts_url
        sts_grant_type = gcp_config.sts_grant_type
        sts_requested_token_type = gcp_config.sts_requested_token_type
        sts_scope = gcp_config.sts_scope
        sts_subject_token_type = gcp_config.sts_subject_token_type
        iam_credentials_url_base = gcp_config.iam_credentials_url_base
        private_key_path = os.environ.get("WIF_PRIVATE_KEY_PATH", os.path.expanduser("~/.ssh/uw_private_key.pem")) # 環境変数優先、なければデフォルトパス
        secret_id = f"{gcp_config.secret_name}-{gcp_config.app_env}"

        if all([project_number, pool_id, provider_id, service_account_email, issuer, private_key_path, secret_id]):
            return _get_secret_with_wif(
                secret_id, 
                project_number, 
                pool_id, 
                provider_id, 
                service_account_email, 
                issuer, 
                private_key_path, 
                sts_url, 
                sts_grant_type, 
                sts_requested_token_type, 
                sts_scope, 
                sts_subject_token_type, 
                iam_credentials_url_base, 
                kid
            )
        else:
            # Workload Identity Federation の設定が不完全な場合
            # 循環参照を避けるため関数内でインポート
            from libcore_hng.utils.app_logger import app_logger
            app_logger.warning("Workload Identity Federation の設定が不完全です。環境変数またはapp_config.jsonを確認してください。")

    # 環境変数または通常のGCP認証で取得
    project_id = gcp_config.project_id if gcp_config.project_id else os.environ.get("GCP_PROJECT_ID")
    secret_name_from_config = gcp_config.secret_name if gcp_config.secret_name else os.environ.get("GCP_SECRET_NAME")
    app_env = gcp_config.app_env if gcp_config.app_env else os.environ.get("APP_ENV", "dev")

    if not project_id or not secret_name_from_config:
        return None

    secret_id = f"{secret_name_from_config}-{app_env}"
    
    try:
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
        response = client.access_secret_version(request={"name": name})
        return response.payload.data
    except Exception as e:
        raise CryptoException(f"GCP Secret Managerからの鍵取得に失敗しました: {e}")

def _get_key(gcp_config: GcpConfig) -> bytes:
    """
    環境変数またはGCP Secret Managerから復号鍵を取得する

    Returns
    -------
    bytes
        復号鍵（バイト列）

    Raises
    ------
    CryptoException
        復号鍵が見つからない場合、または取得時にエラーが発生した場合
    """
    # 1. 環境変数から復号鍵を取得する (最優先: CI/CDやローカルの一時設定用)
    env_key = os.environ.get("APP_SECRET_KEY")
    if env_key:
        return env_key.encode()

    # 2. 環境変数が未設定の場合はGCP Secret Managerから取得する
    #    (Workload Identity Federationが設定されていればそちらを優先)
    gcp_key = _get_gcp_secret_key(gcp_config)
    if gcp_key:
        return gcp_key

    # 鍵が見つからなかった場合
    raise CryptoException(
        "復号鍵が見つかりません。環境変数 \"APP_SECRET_KEY\" または "
        "GCPの設定 (app_config.jsonと環境変数WIF_PRIVATE_KEY_PATH) を確認してください。"
    )

def generate_key_pair() -> dict:
    """
    RSA秘密鍵と公開鍵のペアを生成し、JWK形式の公開鍵を返す。

    Returns
    -------
    dict
        秘密鍵（PEM形式）とJWK形式の公開鍵を含む辞書。
    """
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    public_key = private_key.public_key()
    numbers = public_key.public_numbers()

    def to_base64url(val):
        return base64.urlsafe_b64encode(val.to_bytes((val.bit_length() + 7) // 8, 'big')).decode('utf-8').rstrip('=')

    jwk = {
        "keys": [{
            "kty": "RSA",
            "alg": "RS256",
            "use": "sig",
            "kid": "wif-key-01", # 任意のID
            "n": to_base64url(numbers.n),
            "e": to_base64url(numbers.e)
        }]
    }

    return {
        "private_key_pem": private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ).decode('utf-8'),
        "public_key_jwk": jwk
    }

def load_secret(file_path: Union[str, Path]) -> bytes:
    """
    暗号化されたファイルを読み込み、復号して内容を返す

    Parameters
    ----------
    file_path : str or Path
        暗号化されたファイルのパス

    Returns
    -------
    bytes
        復号されたデータ（バイト列）

    Raises
    ------
    CryptoException
        ファイルの読み込みまたは復号に失敗した場合
    """
    # 循環参照を避けるため関数内でインポート
    import libcore_hng.utils.app_core as app
    if app.core:
        return load_secret_with_gcp_config(file_path, app.core.config.gcp.model_dump())
    else:
        # app.core が初期化されていない場合は、GCP設定なしでキーを取得しようとする
        # これは例えば、設定ファイル自体が暗号化されているようなケースで発生し得る
        # その場合、環境変数APP_SECRET_KEY頼りになるため、注意が必要。
        # もしくは、暗号化された設定ファイルは app.core 初期化前に読まないという運用にする。
        from libcore_hng.utils.app_logger import app_logger
        app_logger.warning("app.core が未初期化のため、GCP Secret Managerの設定が利用できません。環境変数APP_SECRET_KEYを確認してください。")
        return load_secret_with_gcp_config(file_path, {})

def load_secret_with_gcp_config(file_path: Union[str, Path], gcp_config_dict: Dict[str, Any]) -> bytes:
    """
    暗号化されたファイルを読み込み、指定されたGCP設定を使って復号して内容を返す

    Parameters
    ----------
    file_path : str or Path
        暗号化されたファイルのパス
    gcp_config_dict : Dict[str, Any]
        GCP設定を格納した辞書

    Returns
    -------
    bytes
        復号されたデータ（バイト列）

    Raises
    ------
    CryptoException
        ファイルの読み込みまたは復号に失敗した場合
    """
    try:
        # 復号鍵を取得する
        gcp_config = GcpConfig(**gcp_config_dict) # 辞書からGcpConfigモデルを生成
        key = _get_key(gcp_config)
        
        # 暗号化されたファイルを開く
        with Path(file_path).open("rb") as f:
            encrypted = f.read()
        
        # 設定ファイルを復号化
        raw_data = Fernet(key).decrypt(encrypted)
        
        return raw_data
    except CryptoException:
        # _get_key で発生した CryptoException はそのまま投げる
        raise
    except (InvalidToken, Exception) as e:
        # サードパーティの例外やIOエラーをラップして再送出
        raise CryptoException(e)
