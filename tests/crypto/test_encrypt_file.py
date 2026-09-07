import libcore_hng.utils.crypto as crypto

key = crypto.create_encryption_file("tests/crypto/enc_file/test-sample.json")
print(key)
