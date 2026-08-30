import libcore_hng.utils.app_core as app
from configs.runpod import RunPodOverrideConfig

# アプリ初期化処理(import時に1度だけ実行される)
app.init_app(RunPodOverrideConfig, __file__)
config = app.get_config(RunPodOverrideConfig)