import json
import libcore_hng.utils.app_core as app
from libcore_hng.utils.secret_manager import load_secret
from libcore_hng.core.base_config import BaseConfig

# アプリ初期化
app.init_app(BaseConfig, __file__, "app_config.json")
print(app.core.config.gcp.wif_enabled)

# 暗号化された設定ファイルのパス
ENCRYPTED_CONFIG_PATH = app.core.config.project_root_path / "configs" / "test-config.json.enc"

def decrypt_config_example():
    try:
        # secret_manager.pyのload_secret関数を使ってファイルを復号
        decrypted_bytes = load_secret(ENCRYPTED_CONFIG_PATH)
        decrypted_content = decrypted_bytes.decode("utf-8")

        print("復号されたコンテンツ:")
        print(decrypted_content)

        # もしJSONファイルであれば、JSONとしてロードして内容を確認することも可能
        config_data = json.loads(decrypted_content)
        print("JSONとしてロードされたデータ:")
        print(json.dumps(config_data, indent=2, ensure_ascii=False))

    except Exception as e:
        print(f"復号中にエラーが発生しました: {e}")

if __name__ == "__main__":
    # WIF_PRIVATE_KEY_PATH 環境変数を設定してください
    # 例: os.environ["WIF_PRIVATE_KEY_PATH"] = "/path/to/your/private_key.pem"
    # このスクリプトを実行する前に、必要に応じて環境変数を設定してください。
    decrypt_config_example()
