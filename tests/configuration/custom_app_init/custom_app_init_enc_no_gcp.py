import libcore_hng.utils.app_core as app
from configs.extension_config import ExtendedConfig

# アプリ初期化処理(import時に1度だけ実行される)
app.init_app(ExtendedConfig, __file__, "app_config.json", "app_config_ext.json", "test-config.json.enc")
config = app.get_config(ExtendedConfig)