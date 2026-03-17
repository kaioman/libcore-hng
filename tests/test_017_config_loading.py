import libcore_hng.utils.app_core as app
from libcore_hng.core.base_config import BaseConfig

# アプリ初期化
app.init_app(BaseConfig, __file__, "app_config.json")

# 読み込み内容の確認
print(app.core.config.logging)
print(app.core.config.gcp)
