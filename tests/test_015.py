import test_013_appinit as app
import libcore_hng.utils.app_logger as app_logger

# アプリ初期化
app.init_app(__file__, "app_config.json", "app_config_override.json")

# プロジェクトルートパス確認
# ロガーテスト
app_logger.info(app.core.config.logging.log_error_string)
app_logger.info(app.core.config.test.append_member)