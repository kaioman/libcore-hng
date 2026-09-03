from __future__ import annotations

from pathlib import Path
from typing import TypedDict

class FileContent(TypedDict):
    """
    ファイルの内容を保持する辞書型

    Attributes
    ----------
    path : Path
        ファイルパス
    content : str
        ファイル内容
    """

    path: Path
    """ ファイルパス """

    content: str
    """ ファイル内容 """

class ProjectInputs(TypedDict):
    """
    プロジェクトの入力ファイルを保持する辞書型

    Attributes
    ----------
    docs : list[FileContent]
        docsフォルダ内のファイル内容リスト
    src : list[FileContent]
        srcフォルダ内のファイル内容リスト
    """

    docs: list[FileContent]
    """ docsフォルダ内のファイル内容リスト """

    src: list[FileContent]
    """ srcフォルダ内のファイル内容リスト """

class DocGaps(TypedDict):
    """
    ドキュメントの差分を保持する辞書型

    Attributes
    ----------
    missing_sections : list[str]
        ドキュメントが不足しているセクションリスト
    outdated_content : list[Path]
        古いコンテンツが含まれているファイルパスリスト
    """

    missing_sections: list[str]
    """ ドキュメントが不足しているセクションリスト """

    outdated_content: list[str]
    """ 古いコンテンツが含まれているファイルパスリスト """

    new_implementations: list[str]
    """ 新しい実装が含まれているファイルパスリスト """
    