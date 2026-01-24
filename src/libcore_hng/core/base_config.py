import json
import os
from pathlib import Path
from typing import TypeVar
from libcore_hng.core.base_config_model import BaseConfigModel
from libcore_hng.configs.logger import LoggerConfig
from libcore_hng.utils.system import find_project_root

T = TypeVar("T", bound="BaseConfig")

class BaseConfig(BaseConfigModel):
    
    logging: LoggerConfig = LoggerConfig()
    """ ロガー共通設定 """

    project_root_path: Path = Path(".")
    """ プロジェクトルートパス """
    
    @classmethod
    def load_config(cls: type[T], caller_file: str, *file_names: str, optional_config_dir: Path | None = None) -> T:
        """
        設定ファイルを読み込む
        
        Parameters
        ----------

        caller_file : str
            呼び出し元ファイルの__file__
        file_names : str
            設定ファイル名のか可変長引数
        optional_config_dir : Path
            設定ファイルのディレクトリ
            指定時はPathオブジェクトで指定する 例：Path("path/to/configs")
        """
        
        if optional_config_dir is None:
            
            # 設定ファイル格納ディレクトリ名を環境変数から取得
            config_dir_name = "configs"
            if "CONFIG_DIR_NAME" in os.environ:
                config_dir_name = os.environ["CONFIG_DIR_NAME"]
            
            # 環境変数CONFIG_DIRの設定有無を確認
            if "PROJECT_ROOT" in os.environ:
                # 環境変数よりプロジェクトルートパスを取得
                project_root = Path(os.environ["PROJECT_ROOT"]).resolve()
            elif "CONFIG_DIR" in os.environ:
                # 環境変数より設定ファイル格納ディレクトリパスを取得
                config_dir_env = Path(os.environ["CONFIG_DIR"]).resolve()
                # プロジェクトルートパスを取得
                project_root = config_dir_env.parent
            else:
                # プロジェクトルートパスを取得
                project_root = find_project_root(Path(caller_file))

            # 設定ファイル格納パスを取得
            config_dir = project_root / config_dir_name

        else:
            config_dir = optional_config_dir

        # 設定ファイルを読み込んでマージする
        merged = {}
        for file_name in file_names:
            config_path = config_dir / file_name
            if config_path.exists():
                with open(config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    merged.update(data)
        instance = cls(**merged)
        
        # プロジェクトルートパスを設定
        instance.project_root_path = project_root
        
        # 自クラスインスタンスを共通設定クラスインスタンスとして返す
        return instance

cfg: BaseConfig | None = None
""" 共通設定クラスインスタンス """