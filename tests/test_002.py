import test_002_config

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
