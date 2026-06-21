import argparse
import subprocess
import tempfile
from pathlib import Path
from libcore_hng.utils.crypto import create_decryption_file, create_encryption_file

def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Decrypt .enc, edit in Notepad, then re-encrypt."
    )
    parser.add_argument("encrypt_file", help="Encrypted input file (.enc)")
    parser.add_argument(
        "-k",
        "--secret-key",
        required=True,
        help="Fernet secret key"
    )
    return parser.parse_args(argv)

def run(secret_key: str, encrypt_file_str: str) -> None:
    """
    暗号化ファイルをメモ帳で開き編集可能にして保存後に再度暗号化する

    Parameters
    ----------
    secret_key : str
        秘密鍵
    encrypt_file_str : str
        暗号化ファイルパス

    """

    # 暗号化ファイルの格納ディレクトリ取得
    encrypt_file_path = Path(encrypt_file_str)
    if not encrypt_file_path.exists():
        print(f"[ERROR] 指定された暗号化ファイルが見つかりません: {encrypt_file_str}")
        return

    # 処理開始
    print(f"[INFO] 処理を開始します。対象ファイル: {encrypt_file_path.name}")

    # OSが管理する安全な一時ディレクトリ使用
    is_success = True
    with tempfile.TemporaryDirectory() as tmp_dir:
        
        # 一時ファイルのパスを設定する
        tmp_json_path = Path(tmp_dir) / encrypt_file_path.stem
        tmp_json_str = str(tmp_json_path)

        try:
            # 暗号化ファイルを復号して一時ファイルとして出力
            print(f"[PROCESS] ファイルを復号中...")
            create_decryption_file(encrypt_file_str, tmp_json_str, secret_key)
            print(f"[SUCCESS] 復号が完了しました。一時ファイルを生成しました。")

            # 復号ファイルチェック
            if not tmp_json_path.exists():
                raise FileNotFoundError("復号ファイルの一時出力に失敗しました。")

            # メモ帳編集
            print(f"[WAIT] メモ帳を起動します。編集を完了し、上書き保存してメモ帳を閉じてください。")
            orig_mtime = tmp_json_path.stat().st_mtime

            # メモ帳プロセス実行
            subprocess.run(["notepad.exe", tmp_json_path], check=True)
            print(f"[INFO] メモ帳が閉じられました。")

            # 変更チェックと再暗号化
            if tmp_json_path.stat().st_mtime == orig_mtime:
                print(f"[WARNING] ファイルに変更されませんでした。再暗号化をスキップします。")
            else:
                print(f"[PROCESS] ファイル変更を検知しました。ファイルを再暗号化しています...")
                # 編集したjsonファイルを暗号化する
                create_encryption_file(tmp_json_str, str(encrypt_file_path), secret_key)
                print(f"[SUCCESS] 暗号化ファイルの更新が完了しました。")
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] メモ帳の起動、または実行中にエラーが発生しました: {e}")
            is_success = False
        except Exception as e:
            print(f"[ERROR] 処理中に予期せぬエラーが発生しました: {e}")
            import traceback
            # デバッグ用の詳細なスタックトレース出力
            print(traceback.format_exc())
            is_success = False

    if is_success:
        print(f"[INFO] 一時ファイルを削除しました。暗号化ファイルの編集が完了しました。")
    else:
        print(f"[WARNING] 処理中にエラーが発生したため、暗号化ファイルの編集は未完了のまま一時ファイルを強制削除しました。")
        
def main(argv=None) -> int:
    args = parse_args(argv)
    run(args.secret_key, args.encrypt_file)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
