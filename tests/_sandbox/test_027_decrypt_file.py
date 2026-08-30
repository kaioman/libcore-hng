import libcore_hng.utils.app_core as app
import libcore_hng.utils.crypto as crypto
from libcore_hng.core.base_config import BaseConfig

# アプリ初期化
app.init_app(BaseConfig, __file__, "app_config.json")

# 設定ファイルを暗号化して新規ファイルとして作成
# 第三引数に秘密鍵を渡す。
crypto.create_decryption_file("tests/enc_file/test-config.json.enc", "tests/enc_file/test-config.json", "xxxxxx")
