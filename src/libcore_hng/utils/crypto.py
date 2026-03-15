from cryptography.fernet import Fernet

def generate_key() -> bytes:
    """
    暗号化用のキーを生成する
    
    Returns
    -------
    bytes
        生成されたキー
    """
    return Fernet.generate_key()

def create_encryption_file(file_path: str) -> bytes:
    """
    指定されたファイルを暗号化し、拡張子 .enc を付与して保存する
    
    Parameters
    ----------
    file_path : str
        暗号化する対象ファイルのパス
        
    Returns
    -------
    bytes
        暗号化に使用したキー
    """
    key = generate_key()
    with open(file_path, "rb") as f:
        data = f.read()
        
    encrypted = Fernet(key).encrypt(data)
    with open(f"{file_path}.enc", "wb") as f:
        f.write(encrypted)

    return key
