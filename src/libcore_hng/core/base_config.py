import json
import os
from pathlib import Path
from typing import TypeVar, Dict, Any
from libcore_hng.core.base_config_model import BaseConfigModel
from libcore_hng.configs.logger import LoggerConfig
from libcore_hng.configs.gcp import GcpConfig
from libcore_hng.utils.system import find_project_root

T = TypeVar("T", bound="BaseConfig")

class BaseConfig(BaseConfigModel):
    
    logging: LoggerConfig = LoggerConfig()
    """ ロガー共通設定 """

    gcp: GcpConfig = GcpConfig()
    """ Google Cloud Platform 設定 """

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
                # 環境変数より設定ファイル格納ディレクトリパスを取得(プロジェクトルートと兼用とする。CONFIG_DIRは将来廃止予定)
                project_root = Path(os.environ["CONFIG_DIR"]).resolve()
            else:
                # プロジェクトルートパスを取得
                project_root = find_project_root(Path(caller_file))

            # 設定ファイル格納パスを取得
            config_dir = project_root / config_dir_name

        else:
            config_dir = optional_config_dir

        # 設定ファイルを読み込んでマージする
        merged: Dict[str, Any] = {}
        loaded_config_files = [] # 正常に読み込まれた設定ファイル名を保持

        # 統合された設定ファイルを読み込む
        for file_name in file_names:
            config_path = config_dir / file_name
            if not config_path.exists():
                # ファイルが存在しない場合はエラーログを出力し、例外を発生させる
                from libcore_hng.exceptions import ConfigurationException
                
                # app_config.json の内容を取得
                app_config_content = "N/A"
                
                # app_config.jsonのサンプル内容を用意
                app_config_sample_data = {
                    "logging": {
                        "logfile_name": "libcore-hng.log",
                        "logfile_name_suffix": 0,
                        "logfolder_name": "./log",
                        "logformat": "%(levelname)-7s : %(asctime)s : %(message)s",
                        "loglevel": 20,
                        "log_prefix_format": "[ {} {} ]",
                        "log_depth": "+",
                        "log_interval": 1,
                        "log_backupCount": 7,
                        "log_rotation_when": "midnight",
                        "log_file_encording": "utf-8",
                        "log_rotation_utc_time": False  # Pythonでは大文字のFalse
                    },
                    "gcp": {
                        "project_id": "test-project",
                        "secret_name": "test-secret"
                    }
                }
                app_config_sample = json.dumps(app_config_sample_data, indent=2, ensure_ascii=False)

                # app_config.jsonが存在する場合は内容を読み込む
                app_config_content = f"ファイルが存在しません。以下の内容で作成してください。\n```json\n{app_config_sample}\n```"

                files_str =  ' '.join(loaded_config_files) if loaded_config_files else 'なし'
                error_message = (
                    f"設定ファイル `{file_name}` が見つかりません。\n"
                    f"現在の設定ディレクトリ: `{config_dir}`\n"
                    f"読み込まれた設定ファイル: `{files_str}`\n"
                    f"app_config.json の内容（サンプル）:\n{app_config_content}"
                )
                print(error_message)
                raise ConfigurationException(error_message)

            if file_name.endswith(".enc"):
                # --- 暗号化ファイル (.enc) の場合 ---
                # 循環参照を避けるため関数内でインポート
                from libcore_hng.utils.secret_manager import load_secret
                
                # ファイルを復号化
                raw_bytes = load_secret(config_path)
                data = json.loads(raw_bytes.decode("utf-8"))
                merged.update(data)
            else:
                # --- 通常のJSONファイルの場合 ---
                with open(config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    merged.update(data)
            loaded_config_files.append(file_name) # 正常に読み込まれたファイル名を追加
                    
        instance = cls(**merged)
        
        # プロジェクトルートパスを設定
        instance.project_root_path = project_root
        
        # 自クラスインスタンスを共通設定クラスインスタンスとして返す
        return instance

cfg: BaseConfig | None = None
""" 共通設定クラスインスタンス """
