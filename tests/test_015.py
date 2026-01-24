import os
import test_013_appinit as app
import libcore_hng.utils.app_logger as app_logger

# CONFIG_DIR環境変数を設定
#os.environ["CONFIG_DIR"] = 'E:/Dev/030 libcore-hng/libcore-hng/configs'
#os.environ["PROJECT_ROOT"] = 'E:/Dev/030 libcore-hng/libcore-hng'

# アプリ初期化
app.init_app(__file__, "logger.json", "override.json")

# プロジェクトルートパス確認
# ロガーテスト
app_logger.info(app.core.config.project_root_path)