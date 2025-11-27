import test_002_config
import libcore_hng.utils.app_logger as app_logger
import test_002_sub

def test_load_config():
    test_002_config.cfg = test_002_config.DerivedConfig.load_config(
        __file__,
        "logger.json",
        "override.json"
    )

# 設定読込
test_load_config()

# 設定をprint出力
print(test_002_config.cfg.test.append_member)

# ロガー設定
app_logger.setting(test_002_config.cfg)

# メソッド実行テスト
t002 = test_002_config.Test()
t002.log_test()

# 別ファイルのメソッド実行
test_002_sub.test_002_sub_method()
