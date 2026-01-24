import os
import test_013_sub as t013
import test_013_appinit as app

# 環境変数
os.environ["PROJECT_ROOT"] = "E:\\Dev\\028 flaskion\\flaskion\\flaskion"

# アプリ初期化
app.init_app(__file__, "logger.json", "override.json")
# 拡張メンバ確認
print(app.core.config.test.append_member)

# 別ファイル関数でのapp参照テスト
t013.test013()
