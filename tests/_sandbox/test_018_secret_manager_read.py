import os
from pathlib import Path
from google.cloud import secretmanager

### 検証用コードのため動作しない

BASE_DIR = Path(__file__).resolve().parent.parent
auth_file = BASE_DIR / "auth" / "dev-auth.json"

# 環境変数にdev-auth.jsonのパスを設定
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(auth_file)

def get_secret_test():
    try:
        # Secret Managerクライアントの作成
        client = secretmanager.SecretManagerServiceClient()
        
        # プロジェクトIDとシークレットIDを指定
        project_id = "gen-lang-client-0452718754"
        secret_id= "DECRYPTION_KEY_DEV"
        
        # シークレットの完全なリソース名を作成
        resource_name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"

        # シークレットへのアクセス
        response = client.access_secret_version(request={"name": resource_name})
        payload = response.payload.data.decode("UTF-8")
        
        print(f"Retrieved secret: {payload}")
        
    except Exception as e:
        print(f"Error: {e}")
        
if __name__ == "__main__":
    get_secret_test()