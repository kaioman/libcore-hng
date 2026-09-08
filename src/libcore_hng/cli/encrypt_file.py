import argparse
import getpass
from pathlib import Path
from libcore_hng.utils.crypto import create_encryption_file

def parse_args(argv: list[str] | None = None):
    parser = argparse.ArgumentParser(
        description="Encrypt a file with Fernet."
    )
    parser.add_argument(
        "src_file", 
        help="暗号化するファイルのパス"
    )
    parser.add_argument(
        "-o",
        "--output",
        help="暗号化ファイルの出力先。指定しない場合は、元のファイルと同じディレクトリに .enc 拡張子を付与して保存される。",
    )
    return parser.parse_args(argv)

def run(src_file: str, output_file: str | None) -> int:
    """
    指定されたファイルを暗号化する

    Parameters
    ----------
    src_file : str
        暗号化するファイルのパス
    output_file : str | None
        暗号化ファイルの出力先。None の場合は、元のファイルと同じディレクトリに .enc 拡張子を付与して保存される。
    """

    # 入力ファイルの存在確認
    src_file_path = Path(src_file)
    if not src_file_path.is_file():
        print(f"[ERROR] 指定された入力ファイルが見つかりません: {src_file}")
        return 1

    try:
        # 出力ファイルのパスを決定
        default_output_path = src_file_path.with_suffix(
            src_file_path.suffix + ".enc"
        )
        output_path = (
            Path(output_file)
            if output_file else default_output_path
        )

        # 入力ファイル自身への上書きを防ぐ
        if output_path.resolve() == src_file_path.resolve():
            print(f"[ERROR] 入力ファイルと出力ファイルが同じです。上書きはできません。")
            return 1

        # create_encryption_file は内部で .enc を生成するため、
        # 既定の出力先と同じ場合は移動先を指定しない
        dest_file_path = (
            None
            if output_path.resolve() == default_output_path.resolve() else str(output_path)
        )

        # 出力先ディレクトリの存在確認
        if not output_path.parent.is_dir():
            print(f"[ERROR] 出力先ディレクトリが存在しません: {output_path.parent}")
            return 1
        
        # 秘密鍵の入力を促す
        secret_key = getpass.getpass("秘密鍵を貼り付けてください。新規で生成する場合は Enter を押してください: ")
        key = secret_key if secret_key else None

        # 暗号化処理
        encryption_key = create_encryption_file(
            str(src_file_path), 
            dest_file_path, 
            key
        )

        # 成功メッセージの表示
        print(f"[SUCCESS] ファイルを暗号化しました。出力先: {output_path}")

        # 生成された秘密鍵を表示
        if key is None:
            print(f"[WARNING] 新しい秘密鍵が生成されました。安全な場所に保管してください。")
            print(f"秘密鍵: {encryption_key.decode('utf-8')}")

        return 0

    except Exception as e:
        print(f"[ERROR] 暗号化中にエラーが発生しました: {e}")
        return 1

def main(argv=None) -> int:
    """
    メイン関数
    """
    args = parse_args(argv)
    return run(args.src_file, args.output)

if __name__ == "__main__":
    raise SystemExit(main())