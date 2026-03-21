import json
from libcore_hng.utils import secret_manager

# 鍵ペアを生成
key_pair = secret_manager.generate_key_pair()

# 秘密鍵をファイルに保存
with open("private_key.pem", "w") as f:
    f.write(key_pair["private_key_pem"])

# 公開鍵をJWK形式で表示
print("--- 以下のJSONをGCPコンソールの『JWK ファイル』欄にアップロード、または貼り付けてください ---")
print(json.dumps(key_pair["public_key_jwk"], indent=2))
print("--------------------------------------------------------------------------------")
print("秘密鍵は 'private_key.pem' として保存されました。大切に保管してください。")
