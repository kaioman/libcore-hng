from cryptography.fernet import Fernet
from libcore_hng.configs.gcp import GcpConfig
from libcore_hng.utils.secret_manager import _get_gcp_secret_key
from typing import Optional

def generate_key() -> bytes:
    """
    暗号化用のキーを生成する
    
    Returns
    -------
    bytes
        生成されたキー
    """
    return Fernet.generate_key()

def create_encryption_file(file_path: str, key: bytes | str | None = None) -> bytes:
    """
    指定されたファイルを暗号化し、拡張子 .enc を付与して保存する

    Parameters
    ----------
    file_path : str
        暗号化する対象ファイルのパス
    key : bytes | str | None, optional
        暗号化に使用するキー。指定しない場合は新しく生成される, by default None

    Returns
    -------
    bytes
        暗号化に使用したキー
    """
    if key is None:
        key = generate_key()
    elif isinstance(key, str):
        key = key.encode("utf-8")

    with open(file_path, "rb") as f:
        data = f.read()

    encrypted = Fernet(key).encrypt(data)
    with open(f"{file_path}.enc", "wb") as f:
        f.write(encrypted)

    return key

def create_encryption_file_from_secret_manager(file_path: str, secret_name: str) -> bytes:
    """
    指定されたファイルを暗号化し、GCP Secret Managerから取得した鍵を使用して拡張子 .enc を付与して保存する。

    Parameters
    ----------
    file_path : str
        暗号化する対象ファイルのパス
    secret_name : str
        GCP Secret Managerから取得する鍵のシークレット名

    Returns
    -------
    bytes
        暗号化に使用したキー
    """
    # app_coreが初期化されていることを前提とする
    import libcore_hng.utils.app_core as app
    if not app.core or not app.core.config or not app.core.config.gcp:
        raise ValueError("app_coreが初期化されていないか、GCP設定がありません。")

    # Secret Managerから鍵を取得
    gcp_config = app.core.config.gcp.model_copy(update={"secret_name": secret_name})
    key = _get_gcp_secret_key(gcp_config)
    
    if not key:
        raise ValueError(f"Secret Managerから鍵 '{secret_name}' を取得できませんでした。")

    return create_encryption_file(file_path, key)
