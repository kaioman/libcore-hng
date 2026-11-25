import sys
import json
import argparse
from pathlib import Path
from typing import Any
from pydantic import ValidationError
from libcore_hng.configs.directory_tree import DirectoryTreeConfig
from libcore_hng.core.base_config_model import BaseConfigModel
from libcore_hng.utils.directory_tree import render_directory_tree

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """
    コマンドライン引数を解析する

    Parameters
    ----------
    argv : list[str] | None
        コマンドライン引数のリスト。None の場合は sys.argv[1:] を使用する

    Returns
    -------
    argparse.Namespace
        解析された引数の名前空間    
    """

    # argparse.ArgumentParser を作成し、コマンドライン引数を定義する
    parser = argparse.ArgumentParser(
        description="ディレクトリ構成をツリーまたはExcel向けTSVで出力します"        
    )

    # コマンドライン引数を定義する
    parser.add_argument("directory", type=Path, help="表示するディレクトリ")
    parser.add_argument(
        "--style",
        choices=("normal", "stylish"),
        default="normal",
        help="ツリーの罫線スタイル",
    )
    parser.add_argument(
        "--format",
        choices=("tree", "excel"),
        default="tree",
        help="出力形式。excel は Excel に貼り付け可能は TSV 形式です",        
    )
    parser.add_argument(
        "--exclude-dir",
        action="append",
        default=[],
        metavar="NAME",
        help="除外するフォルダ名。複数回指定できます",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help="directory-tree 専用の JSON設定ファイル",        
    )

    # コマンドライン引数を解析して返す
    return parser.parse_args(argv)

def _warn_unknown_keys(
    data: Any,
    model: type[BaseConfigModel],
    prefix: str = "",
) -> None:
    """
    未定義の設定キーが存在する場合に警告を表示する

    Parameters
    ----------
    data : Any
        設定データ
    model : type[BaseConfigModel]
        設定モデルの型
    prefix : str, optional
        設定キーのプレフィックス, by default ""
    """

    # 未定義の設定キーが存在する場合に警告を表示する
    if not isinstance(data, dict):
        return

    for key, value in data.items():
        key_path = f"{prefix}.{key}" if prefix else key
        field_type = model.__annotations__.get(key)
        if field_type is None:
            print(
                f"[WARNING] 未定義の設定キー '{key_path}' を無視します。"
                "該当する設定には既定値を使用します。",
                file=sys.stderr,
            )
            continue

        if (
            isinstance(field_type, type)
            and issubclass(field_type, BaseConfigModel)
        ):
            _warn_unknown_keys(value, field_type, key_path)
        
def _load_config(config_path: Path | None) -> DirectoryTreeConfig:
    """
    設定ファイルを読み込む

    Parameters
    ----------
    config_path : Path | None
        設定ファイルのパス。None の場合は既定値を使用する

    Returns
    -------
    DirectoryTreeConfig
        読み込まれた設定データ
    """

    # 設定ファイルが指定されていない場合は既定値を使用する
    if config_path is None:
        return DirectoryTreeConfig()

    # 設定ファイルを読み込む
    path = config_path.expanduser()
    if not path.is_file():
        raise FileNotFoundError(f"設定ファイルが見つかりません: {path}")

    # 設定ファイルを JSON として読み込む
    data: Any = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("directory-tree 設定のルートは JSON オブジェクトにしてください")

    # 未定義の設定キーが存在する場合に警告を表示する
    _warn_unknown_keys(data, DirectoryTreeConfig)

    # 設定データを DirectoryTreeConfig に変換して返す
    return DirectoryTreeConfig(**data)

def main(argv: list[str] | None = None) -> int:
    """
    ディレクトリ構成をツリーまたはExcel向けTSVで出力するコマンドラインインターフェースのエントリーポイント

    Parameters
    ----------
    argv : list[str] | None
        コマンドライン引数のリスト。None の場合は sys.argv[1:] を使用する

    Returns
    -------
    int
        終了コード。0 は正常終了、1 はエラー終了を示す
    """

    # コマンドライン引数を解析する
    args = parse_args(argv)
    try:
        # 設定ファイルを読み込む
        config = _load_config(args.config)
        # ディレクトリ構成をツリーまたはExcel向けTSVで出力する
        output = render_directory_tree(
            directory=args.directory,
            style=args.style,
            output_format=args.format,
            excluded_dirs=args.exclude_dir,
            config=config,
        )
    except (OSError, ValueError, ValidationError) as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1

    # 出力結果を表示する
    print(output)

    # 正常終了コードを返す
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
