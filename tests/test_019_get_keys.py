import json
import base64
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

# 1. RSA鍵ペアの生成
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048
)

# 2. 秘密鍵をPEM形式で保存 (Ubuntuに置く「実印」)
with open("private_key.pem", "wb") as f:
    f.write(private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ))

# 3. 公開鍵からJWK形式のパラメータを抽出 (GCPに送る「印鑑証明」)
public_key = private_key.public_key()
numbers = public_key.public_numbers()

def to_base64url(val):
    return base64.urlsafe_b64encode(val.to_bytes((val.bit_length() + 7) // 8, 'big')).decode('utf-8').rstrip('=')

jwk = {
    "keys": [{
        "kty": "RSA",
        "alg": "RS256",
        "use": "sig",
        "kid": "wif-key-01", # 任意のID
        "n": to_base64url(numbers.n),
        "e": to_base64url(numbers.e)
    }]
}

print("--- 以下のJSONをGCPコンソールの『JWK ファイル』欄にアップロード、または貼り付けてください ---")
print(json.dumps(jwk, indent=2))
print("--------------------------------------------------------------------------------")
print("秘密鍵は 'private_key.pem' として保存されました。大切に保管してください。")