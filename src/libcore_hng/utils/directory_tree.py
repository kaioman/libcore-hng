from __future__ import annotations

import os
import re
import ctypes
from collections.abc import Iterable
from functools import cmp_to_key
from pathlib import Path
from typing import Literal
from libcore_hng.configs.directory_tree import TreeBorderStyleConfig, TreeBorderPresetConfig, DirectoryTreeConfig

TreeStyle = Literal["normal", "stylish"]
""" ツリーの罫線スタイルの種類を表す型エイリアス """
TreeFormat = Literal["tree", "excel"]
""" 出力形式の種類を表す型エイリアス """

# Windows の論理的な文字列比較関数をロードする
_WINDOWS_LOGICAL_COMPARE = None
if os.name == "nt":
    _WINDOWS_LOGICAL_COMPARE = ctypes.WinDLL("shlwapi").StrCmpLogicalW
    _WINDOWS_LOGICAL_COMPARE.argtypes = [ctypes.c_wchar_p, ctypes.c_wchar_p]
    _WINDOWS_LOGICAL_COMPARE.restype = ctypes.c_int

def _natural_sort_key(name: str) -> tuple[tuple[int, int | str], ...]:
    """
    文字列を自然順序でソートするためのキーを生成する

    Parameters
    ----------
    name : str
        ソート対象の文字列

    Returns
    -------
    tuple[tuple[int, int | str], ...]
        自然順序でソートするためのキー
    """
    return tuple(
        (0, int(part)) if part.isdigit() else (1, part.casefold())
        for part in re.split(r"(\d+)", name)
        if part
    )

def _compare_entries(left: os.DirEntry[str], right: os.DirEntry[str]) -> int:
    """
    ディレクトリエントリを比較するための関数

    Parameters
    ----------
    left : os.DirEntry[str]
        比較対象の左側のディレクトリエントリ
    right : os.DirEntry[str]
        比較対象の右側のディレクトリエントリ
    """

    # ディレクトリとファイルを区別してソートする
    left_is_dir = left.is_dir(follow_symlinks=False)
    right_is_dir = right.is_dir(follow_symlinks=False)
    if left_is_dir != right_is_dir:
        return -1 if left_is_dir else 1
    
    # Windows の場合は論理的な文字列比較を使用する
    if _WINDOWS_LOGICAL_COMPARE is not None:
        result = _WINDOWS_LOGICAL_COMPARE(left.name, right.name)
        if result:
            return result

    # それ以外の場合は自然順序でソートする
    left_key = _natural_sort_key(left.name)
    right_key = _natural_sort_key(right.name)
    if left_key != right_key:
        return -1 if left_key < right_key else 1

    # それでも同じ場合は通常の文字列比較を使用する
    return (left.name > right.name) - (left.name < right.name)
    
def _tsv_cell(value: str) -> str:
    """
    TSV のセルとして出力するために、タブ、改行、復帰をエスケープする

    Parameters
    ----------
    value : str
        TSV のセルとして出力する文字列
    
    Returns
    -------
    str
        エスケープされた文字列
    """
    return value.replace("\t", "\\t").replace("\r", "\\r").replace("\n", "\\n")

def render_directory_tree(
    directory: Path,
    style: TreeStyle = "normal",
    output_format: TreeFormat = "tree",
    excluded_dirs: Iterable[str] = (),
    config: DirectoryTreeConfig | None = None,
) -> str:
    """
    ディレクトリ構成をツリーまたはExcel向けTSVで出力する

    Parameters
    ----------
    directory : Path
        出力対象のディレクトリのパス
    style : TreeStyle, optional
        ツリーの罫線スタイルの種類, by default "normal"
    output_format : TreeFormat, optional
        出力形式の種類, by default "tree"
    excluded_dirs : Iterable[str], optional
        除外するディレクトリ名のリスト, by default ()
    config : DirectoryTreeConfig | None, optional
        設定データ, by default None
    
    Returns
    -------
    str
        ツリーまたはExcel向けTSVの文字列
    Raises
    ------
    NotADirectoryError
        指定されたパスがディレクトリではない場合に発生する
    """

    # 指定されたパスがディレクトリであることを確認する
    root = directory.expanduser()
    if not root.is_dir():
        raise NotADirectoryError(f"指定されたディレクトリが見つかりません")
    if style not in ("normal", "stylish"):
        raise ValueError(f"未対応のスタイルです: {style}")
    if output_format not in ("tree", "excel"):
        raise ValueError(f"未対応の出力形式です: {output_format}")

    # 設定データを使用する場合は、指定されたスタイルに応じて罫線スタイルを取得する
    tree_config = config or DirectoryTreeConfig()
    borders: TreeBorderStyleConfig = (
        tree_config.borders.normal
        if style == "normal"
        else tree_config.borders.stylish
    )
    excluded_names = {name.casefold() for name in excluded_dirs}
    root_name = root.name or str(root)

    # ツリーの行と Excel 向け TSV の行を格納するリストを初期化する
    tree_lines = [root_name]
    rows = [("0", "directory", root_name, ".")]

    def walk(
        current: Path,
        prefix: str,
        depth: int,
        relative_parent: Path,
    ) -> None:
        """
        ディレクトリを再帰的に走査して、ツリーの行と Excel 向け TSV の行を生成する

        Parameters
        ----------
        current : Path  
            現在のディレクトリのパス
        prefix : str
            ツリーの行の接頭辞
        depth : int
            現在のディレクトリの深さ
        relative_parent : Path
            現在のディレクトリの親ディレクトリからの相対パス
        """

        # ディレクトリ内のエントリを取得して、除外対象のディレクトリを除外する
        with os.scandir(current) as iterator:
            entries = list(iterator)

        # 除外対象のディレクトリを除外する
        entries = [
            entry
            for entry in entries
            if not (
                entry.is_dir(follow_symlinks=False)
                and entry.name.casefold() in excluded_names
            )
        ]
        entries.sort(key=cmp_to_key(_compare_entries))

        # ディレクトリ内のエントリを走査して、ツリーの行と Excel 向け TSV の行を生成する
        for index, entry in enumerate(entries):

            # ディレクトリエントリの情報を取得する
            is_last = index == len(entries) - 1
            is_directory = entry.is_dir(follow_symlinks=False)
            is_link = entry.is_symlink()
            name = entry.name
            relative_path = (relative_parent / name).as_posix()

            # ツリーの行と Excel 向け TSV の行を生成する
            connector = borders.last if is_last else borders.branch
            tree_lines.append(f"{prefix}{connector}{name}")
            rows.append((
                str(depth + 1),
                "link" if is_link else "directory" if is_directory else "file",
                name,
                relative_path,
            ))

            # ディレクトリの場合は再帰的に走査する
            if is_directory:
                continuation = borders.blank if is_last else borders.vertical
                walk(
                    Path(entry.path),
                    prefix + continuation,
                    depth + 1,
                    relative_parent / name,
                )

    # ディレクトリを再帰的に走査して、ツリーの行と Excel 向け TSV の行を生成する
    walk(root, "", 0, Path())

    # 出力形式に応じて、ツリーまたはExcel向けTSVの文字列を生成して返す
    if output_format == "tree":
        return "\n".join(tree_lines)

    # Excel向けTSVの文字列を生成する
    table = [("depth", "type", "name", "relative_path"), *rows]

    # Excel向けTSVの文字列を生成して返す
    return "\n".join(
        "\t".join(_tsv_cell(value) for value in row)
        for row in table
    )
