import libcore_hng.utils.app_core as app
from configs.override_config import OverrideAppConfig

# アプリ初期化処理(import時に1度だけ実行される)
app.init_app(OverrideAppConfig, __file__, "app_config.json", "app_config_override.json")
config = app.get_config(OverrideAppConfig)