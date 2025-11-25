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
