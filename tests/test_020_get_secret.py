import os
import time
import jwt
import json
import requests
import google.oauth2.credentials
from google.cloud import secretmanager

# --- 【設定値】ここを書き換えてください ---
PROJECT_NUMBER = "432034677652"
POOL_ID = "uw-prem-dev-pool"
PROVIDER_ID = "google-oidc-dev-provider"
SERVICE_ACCOUNT_EMAIL = "uw-secret-dev@gen-lang-client-0452718754.iam.gserviceaccount.com"
SECRET_ID = "DECRYPTION_KEY-dev"

# GCP側で設定した Issuer URL (1文字でも違うとNG)
ISSUER = "https://unchainworks.local" 
# 秘密鍵のパス
PRIVATE_KEY_PATH = os.path.expanduser("~/.ssh/uw_private_key.pem")
# ---------------------------------------

def generate_subject_token():
    """秘密鍵で署名した自前JWTを生成する"""
    now = int(time.time())
    with open(PRIVATE_KEY_PATH, "rb") as f:
        private_key_pem = f.read()

    payload = {
        "iss": ISSUER,
        "sub": "ubuntu-server-user", # 管理しやすい任意の識別子
        "aud": f"https://iam.googleapis.com/projects/{PROJECT_NUMBER}/locations/global/workloadIdentityPools/{POOL_ID}/providers/{PROVIDER_ID}",
        "iat": now,
        "exp": now + 3600, # 有効期限1時間
    }

    # RS256で署名してJWTを作成
    headers = {"kid": "wif-key-01"} # gen_keys.py で指定した kid と一致させる
    return jwt.encode(payload, private_key_pem, algorithm="RS256", headers=headers)

def get_secret_with_wif():
    # 1. 自前JWT（Subject Token）を作成
    subject_token = generate_subject_token()

    # 2. Google STS エンドポイントに投げて、Googleの一時トークンに交換
    sts_url = "https://sts.googleapis.com/v1/token"
    data = {
        "audience": f"//iam.googleapis.com/projects/{PROJECT_NUMBER}/locations/global/workloadIdentityPools/{POOL_ID}/providers/{PROVIDER_ID}",
        "grantType": "urn:ietf:params:oauth:grant-type:token-exchange",
        "requestedTokenType": "urn:ietf:params:oauth:token-type:access_token",
        "scope": "https://www.googleapis.com/auth/cloud-platform",
        "subjectToken": subject_token,
        "subjectTokenType": "urn:ietf:params:oauth:token-type:jwt",
    }
    
    response = requests.post(sts_url, data=data)
    response.raise_for_status()
    federated_token = response.json()["access_token"]

    # 3. サービスアカウントになりすます (Impersonation)
    # ※ federated_token を使って、本来のサービスアカウントの権限を得る
    iam_url = f"https://iamcredentials.googleapis.com/v1/projects/-/serviceAccounts/{SERVICE_ACCOUNT_EMAIL}:generateAccessToken"
    headers = {"Authorization": f"Bearer {federated_token}"}
    payload = {"scope": ["https://www.googleapis.com/auth/cloud-platform"]}
    
    response = requests.post(iam_url, headers=headers, json=payload)
    response.raise_for_status()
    final_access_token = response.json()["accessToken"]

    # 4. 最終的なトークンを使って Secret Manager から値を取得
    client = secretmanager.SecretManagerServiceClient(
        credentials=google.oauth2.credentials.Credentials(final_access_token)
    )
    name = f"projects/{PROJECT_NUMBER}/secrets/{SECRET_ID}/versions/latest"
    response = client.access_secret_version(request={"name": name})

    print(f"--- 認証プロバイダの確認 ---")
    print(f"Token type: {type(client.transport._credentials)}")    

    print(f"成功！シークレットの値: {response.payload.data.decode('UTF-8')}")

if __name__ == "__main__":
    get_secret_with_wif()