import shutil
from cryptography.fernet import Fernet
from libcore_hng.utils.secret_manager import _get_gcp_secret_key

def generate_key() -> bytes:
    """
    暗号化用のキーを生成する
    
    Returns
    -------
    bytes
        生成されたキー
    """
    return Fernet.generate_key()

def create_encryption_file(
        src_file_path: str, 
        dest_file_path: str = None, 
        key: bytes | str | None = None) -> bytes:
    """
    指定されたファイルを暗号化し、拡張子 .enc を付与して保存する

    Parameters
    ----------
    src_file_path : str
        暗号化する対象ファイルのパス
    dest_file_path : str
        作成した暗号化ファイルのコピー先パス(未指定時はコピーしない)
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

    with open(src_file_path, "rb") as f:
        data = f.read()

    encrypted = Fernet(key).encrypt(data)
    with open(f"{src_file_path}.enc", "wb") as f:
        f.write(encrypted)

    if dest_file_path:
        shutil.move(f"{src_file_path}.enc", dest_file_path)

    return key

def create_decryption_file(input_file, output_file, key):
    """
    暗号化されたファイルを復号し、ファイルに保存する

    Parameters
    ----------
    input_file : str
        復号する対象ファイルのパス
    output_file : str
        復号したファイルを保存するファイルパス
    key : bytes
        暗号化に使用するキー

    """

    # Fernetオブジェクトを生成
    f = Fernet(key)

    # 暗号化されたファイルを読み込む
    with open(input_file, "rb") as file:
        encrypted_data = file.read()

    # データを復号する
    decrypted_data = f.decrypt(encrypted_data)

    # 復号されたデータをファイルに出力する
    with open(output_file, "wb") as f:
        f.write(decrypted_data)

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

    # GCP設定の存在チェック
    import libcore_hng.configs.gcp as app_gcp
    if not app_gcp or not app_gcp.gcp_config:
        raise ValueError("GCP設定が見つかりません。app_coreの初期化を確認してください。")
    
    # Secret Managerから鍵を取得
    key = _get_gcp_secret_key(app_gcp.gcp_config)
    
    if not key:
        raise ValueError(f"Secret Managerから鍵 '{secret_name}' を取得できませんでした。")

    return create_encryption_file(file_path, key)
