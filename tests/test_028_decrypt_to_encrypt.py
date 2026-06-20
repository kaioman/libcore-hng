from libcore_hng.cli.decrypt_to_encrypt import run

if __name__ == "__main__":
    secret_key = input("Enter decryption key:")
    encrypt_file = input("Enter encrypt file path(path/to/xxxx.json.enc):")

    run(secret_key, encrypt_file)
