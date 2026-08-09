import libcore_hng.utils.app_core as app
from configs.extension_config import ExtendedConfig

# アプリ初期化処理(import時に1度だけ実行される)
# ファイル指定なし。configsフォルダ内のjsonを全て読込対象とする
app.init_app(ExtendedConfig, __file__)
config = app.get_config(ExtendedConfig)