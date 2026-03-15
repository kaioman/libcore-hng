import libcore_hng.utils.app_core as app
import libcore_hng.utils.crypto as crypto
from libcore_hng.core.base_config import BaseConfig

# アプリ初期化
app.init_app(BaseConfig, __file__, "logger.json")

# 設定ファイルを暗号化して新規ファイルとして作成
key = crypto.create_encryption_file("configs/test-config.json")

# 生成された鍵を表示
print("以下の鍵を GCP Secret Manager (または環境変数 APP_SECRET_KEY) に登録してください:")
print(key.decode("utf-8"))