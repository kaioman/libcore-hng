import test_022_app_init as app

# アプリ初期化
app.init_app(__file__, "app_config.json", "test-config.json.enc", "app_config_override.json")

print(app.core.config.gcp.iam_credentials_url_base)
print(app.core.config.logging.log_error_caption_emoji)
print(app.core.config.test.dammy_key)
print(app.core.config.test2.dammy_key2)
print(app.core.config.test.dammy_key3)
