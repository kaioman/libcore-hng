import os
from pathlib import Path
from typing import Union, Optional
from google.cloud import secretmanager
from cryptography.fernet import Fernet, InvalidToken
from libcore_hng.exceptions import CryptoException

def _get_gcp_secret() -> Optional[bytes]:
    """
    GCP Secret Managerから復号鍵を取得する
    """
    project_id = os.environ.get("GCP_PROJECT_ID")
    base_secret_name = os.environ.get("GCP_SECRET_NAME")
    app_env = os.environ.get("APP_ENV", "dev") # デフォルトは dev

    if not project_id or not base_secret_name:
        return None

    secret_id = f"{base_secret_name}-{app_env}"
    
    try:
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
        response = client.access_secret_version(request={"name": name})
        return response.payload.data
    except Exception as e:
        raise CryptoException(f"GCP Secret Managerからの鍵取得に失敗しました: {e}")

def _get_key() -> bytes:
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
    gcp_key = _get_gcp_secret()
    if gcp_key:
        return gcp_key

    # 鍵が見つからなかった場合
    raise CryptoException(
        "復号鍵が見つかりません。環境変数 'APP_SECRET_KEY' または "
        "'GCP_PROJECT_ID' および 'GCP_SECRET_NAME' を確認してください。"
    )

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
    try:
        # 復号鍵を取得する
        key = _get_key()
        
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
