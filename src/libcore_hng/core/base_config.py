import json
import os
import re
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
        loaded_config_files: list[str] = []  # 正常に読み込まれた設定ファイル名を保持

        # file_names が指定されている場合だけ、そのファイルを対象にする
        if file_names:
            config_paths = [config_dir / file_name for file_name in file_names]
        else:
            discover_json_paths = sorted(config_dir.glob("*.json"))
            discover_enc_paths = sorted(config_dir.glob("*.enc"))
            config_paths = [*discover_json_paths, *discover_enc_paths]

        # 環境名称を取得
        current_app_env = os.environ.get("APP_ENV")
        # 環境別設定ファイルのリストを作成
        env_specific_enc_files = [
            p.name
            for p in config_paths
            if p.name.endswith(".enc") and _looks_like_env_specific_config(p.name, current_app_env)
        ]

        # 統合された設定ファイルを読み込む
        for config_path in config_paths:
            file_name = config_path.name
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
                        "logfolder_name": "./logs",
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

                files_str = ' '.join(loaded_config_files) if loaded_config_files else 'なし'
                error_message = (
                    f"設定ファイル `{file_name}` が見つかりません。\n"
                    f"現在の設定ディレクトリ: `{config_dir}`\n"
                    f"読み込まれた設定ファイル: `{files_str}`\n"
                    f"app_config.json の内容（サンプル）:\n{app_config_content}"
                )
                print(f"設定ファイル \'{file_name}\' の読み込みに失敗しました。詳細: {error_message}")
                raise ConfigurationException(error_message)
            if file_name.endswith(".enc"):                
                # --- 暗号化ファイル (.enc) の場合 ---
                # 環境別設定ファイルがある場合は、そちらを優先する。ない場合は汎用設定ファイルを復号する
                if not _should_load_encrypted_config(file_name, current_app_env, env_specific_enc_files):
                    print(
                        f"暗号化設定ファイル `{file_name}` は APP_ENV=`{current_app_env}` と一致しないためスキップします。"
                    )
                    continue

                # 循環参照を避けるため関数内でインポート
                from libcore_hng.utils.secret_manager import load_secret_with_gcp_config

                # GCP設定を辞書として渡す
                gcp_config_dict = merged.get("gcp", {})

                try:
                    # ファイルを復号化
                    raw_bytes = load_secret_with_gcp_config(config_path, gcp_config_dict)
                    data = json.loads(raw_bytes.decode("utf-8"))
                    _deep_merge_dict(merged, data)
                except Exception as e:
                    exception_value = getattr(e, "exc_value", None)
                    if exception_value is not None:
                        detail = str(exception_value)
                        if not detail:
                            detail = (
                                f"{type(exception_value).__name__}: "
                                f"{exception_value!r}"
                            )
                    else:
                        detail = str(e) or repr(e)

                    print(
                        f"設定ファイル `{file_name}` の復号に失敗したため"
                        f"スキップします。詳細: {detail}"
                    )
                    continue
            else:
                # --- 通常のJSONファイルの場合 ---
                with open(config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    _deep_merge_dict(merged, data)

            loaded_config_files.append(file_name)  # 正常に読み込まれたファイル名を追加
        
        instance = cls(**merged)
        
        # プロジェクトルートパスを設定
        instance.project_root_path = project_root
        
        # 自クラスインスタンスを共通設定クラスインスタンスとして返す
        return instance

def _deep_merge_dict(base: dict[str, Any], incomiing: dict[str, Any]) -> None:
    for key, value in incomiing.items():
        if (key in base and isinstance(base[key], dict) and isinstance(value, dict)):
            _deep_merge_dict(base[key], value)
        else:
            base[key] = value

def _looks_like_env_specific_config(file_name: str, app_env: str | None) -> bool:
    """
    APP_ENVに対応する設定ファイルか判定する
    
    Parameters
    ----------
    file_name : str
        設定ファイル名
    app_env : str
        環境名称(dev, prodなどの値) 
    
    Returns
    -------
    bool
        判定結果
    """

    # 環境名称が指定されていない＋.encが含まれていない場合はFalse判定
    if not app_env or not file_name.endswith(".enc"):
        return False

    # .encを除去したファイル名を取得
    stem = file_name[:-4].lower()
    env = app_env.lower()

    # 区切り文字の前後に環境名称があるときだけ env-specific とみなす
    pattern = rf"(?:^|[._-]){env}(?:$|[._-])"
    return bool(re.search(pattern, stem))

def _should_load_encrypted_config(file_name: str, app_env: str | None, env_specific_enc_files: list[str]) -> bool:
    """
    APP_ENVに対応する設定ファイルか判定する

    Parameters
    ----------

    file_name : str
        設定ファイル名
    app_env : str
        環境名称(dev, prodなどの値)

    Returns
    -------
    bool
        判定結果
            True  :復号する
            False :復号対象から除外する
    """

    # 環境名称が指定されていない場合はOK判定
    if not app_env:
        return True

    # 設定ファイル名に.encが含まれていない場合はOK判定
    if not file_name.endswith(".enc"):
        return True

    if _looks_like_env_specific_config(file_name, app_env):
        return True

    # この環境用の専用 .enc があるなら、汎用設定ファイルを使わない
    if env_specific_enc_files:
        return False

    # 専用 .enc が無ければ、汎用設定ファイルをフォールバックとして読込対象とする
    return True

cfg: BaseConfig | None = None
""" 共通設定クラスインスタンス """
