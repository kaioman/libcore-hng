import libcore_hng.utils.app_core as app
from libcore_hng.core.base_config import BaseConfig
from libcore_hng.configs.logger import LoggerConfig

class ExtendedExtraConfig(BaseConfig):
    append_member: str = "default"
    dammy_key3: str = "default"
    dammy_key2: str = "default"

class ExtendedLoggerConfig(LoggerConfig):
    ext1: str = "default"

class OverrideConfig(BaseConfig):
    logging: ExtendedLoggerConfig = ExtendedLoggerConfig()
    test: ExtendedExtraConfig = ExtendedExtraConfig()
    test2: ExtendedExtraConfig = ExtendedExtraConfig()

# 設定クラス定義
CONFIG_CLS = OverrideConfig

def init_app(base_file: str, *config_file: str) -> CONFIG_CLS:
    """
    アプリケーションの初期化処理を実行する

    Parameters
    ----------
    base_file : str
        基準となるファイルパス (デフォルト: __file__)
    *config_file : str, optional
        ロガー設定ファイル名やその他設定ファイル
        BaseConfig.load_config にそのまま渡されるため、複数指定可能
    
    Returns
    -------
    CONFIG_CLS
        ロードされた設定インスタンス
    """
    global config
    app.init_app(CONFIG_CLS, base_file, *config_file)
    config = app.get_config(CONFIG_CLS)
    return config

# アプリ初期化処理(import時に1度だけ実行される)
config: CONFIG_CLS = init_app(__file__)
