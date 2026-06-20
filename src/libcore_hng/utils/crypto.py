import subprocess
import tempfile
from pathlib import Path
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

# def decrypt_to_encrypt(secret_key: str, encrypt_file_str: str):
#     """
#     暗号化ファイルをメモ帳で開き編集可能にして保存後に再度暗号化する

#     Parameters
#     ----------
#     secret_key : str
#         秘密鍵
#     encrypt_file_str : str
#         暗号化ファイルパス

#     """

#     # 暗号化ファイルの格納ディレクトリ取得
#     encrypt_file_path = Path(encrypt_file_str)
#     if not encrypt_file_path.exists():
#         print(f"[ERROR] 指定された暗号化ファイルが見つかりません: {encrypt_file_str}")
#         return

#     # 処理開始
#     print(f"[INFO] 処理を開始します。対象ファイル: {encrypt_file_path.name}")

#     # OSが管理する安全な一時ディレクトリ使用
#     with tempfile.TemporaryDirectory() as tmp_dir:
        
#         # 一時ファイルのパスを設定する
#         tmp_json_path = Path(tmp_dir) / encrypt_file_path.stem
#         tmp_json_str = str(tmp_json_path)

#         try:
#             # 暗号化ファイルを復号して一時ファイルとして出力
#             print(f"[PROCESS] ファイルを復号中...")
#             create_decryption_file(encrypt_file_str, tmp_json_str, secret_key)
#             print(f"[SUCCESS] 復号が完了しました。一時ファイルを生成しました。")

#             # 復号ファイルチェック
#             if not tmp_json_path.exists():
#                 raise FileNotFoundError("復号ファイルの一時出力に失敗しました。")

#             # メモ帳編集
#             print(f"[WAIT] メモ帳を起動します。編集を完了し、上書き保存してメモ帳を閉じてください。")
#             orig_mtime = tmp_json_path.stat().st_mtime

#             # メモ帳プロセス実行
#             subprocess.run(["notepad.exe", tmp_json_path], check=True)
#             print(f"[INFO] メモ帳が閉じられました。")

#             # 変更チェックと再暗号化
#             if tmp_json_path.stat().st_mtime == orig_mtime:
#                 print(f"[WARNING] ファイルに変更されませんでした。再暗号化をスキップします。")
#             else:
#                 print(f"[PROCESS] ファイル変更を検知しました。ファイルを再暗号化しています...")
#                 # 編集したjsonファイルを暗号化する
#                 create_encryption_file(tmp_json_str, secret_key)
#                 print(f"[SUCCESS] 暗号化ファイルの更新が完了しました。")
#         except subprocess.CalledProcessError as e:
#             print(f"[ERROR] メモ帳の起動、または実行中にエラーが発生しました: {e}")
#         except Exception as e:
#             print(f"[ERROR] 処理中に予期せぬエラーが発生しました: {e}")
#             import traceback
#             # デバッグ用の詳細なスタックトレース出力
#             print(traceback.format_exc())

#     print(f"[INFO] 一時ファイルを削除しました。暗号化ファイルの編集が完了しました。")