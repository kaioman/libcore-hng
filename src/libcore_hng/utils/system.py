import os
import psutil
from pathlib import Path

def find_project_root(start_path: Path | None = None) -> Path:
    """
    start_pathから親ディレクトリを辿り、pyproject.tomlが存在するディレクトリを返す
    
    Parameters
    ----------

    start_path : Path
        起点ディレクトリ
    """
    
    # pyproject.tomlを探す
    start_path = (start_path or Path(__file__)).resolve()
    for parent in (start_path,) + tuple(start_path.parents):
        if (parent / "pyproject.toml").exists():
            return parent
    
    # 見つからなかった場合はstart_pathを返す
    return start_path

def split_path(full_path: str) -> tuple[str, str]:
    """
    フルパスからディレクトリとファイル名を返す

    Parameters
    ----------
    full_path : str
        対象となるファイルのフルパス

    Returns
    -------
    tuple[str, str]
        (ディレクトリパス, ファイル名)
    """
    dir_path = os.path.dirname(full_path)
    file_name = os.path.basename(full_path)
    return dir_path, file_name

def ensure_extenstion(filename: str, ext: str) -> str:
    """
    ファイル名に指定した拡張子を補完する

    Parameters
    ----------
    file_name : str
        ファイル名（拡張子が付いていない場合は補完される）
    ext : str
        補完する拡張子（例: ".json", ".xlsx"）
        "."は省略して指定

    Returns
    -------
    str
        拡張子を補完したファイル名
    """
    
    # 拡張子を補完する
    if not filename.lower().endswith("." + ext):
            filename += "." + ext
    return filename

def get_disk_usage():
    """
    ディスク使用量(%)
    """
    
    disk = psutil.disk_usage('/')
    
    return disk.percent

def get_disk_free():
    """
    ディスク空き容量(%)
    """

    return 100 - get_disk_usage()
