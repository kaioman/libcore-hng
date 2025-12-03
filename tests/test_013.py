import test_013_sub as t013
import test_013_appinit as app

# アプリ初期化
app.init_app(__file__, "logger.json", "override.json")
# 拡張メンバ確認
print(app.core.config.test.append_member)

# 別ファイル関数でのapp参照テスト
t013.test013()
