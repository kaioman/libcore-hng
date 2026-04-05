# libcore-hng

A lightweight Python core package designed to unify access to diverse AI APIs and libraries. It provides a consistent, scalable foundation for building modular applications with clarity and flexibility.

## アプリ初期処理サンプル

このプロジェクトでは、`AppInitializer` を用いてアプリケーションの初期化処理を行います。  
初期化は一度だけ実行し、以降はグローバルインスタンス `app_core` を参照してください。

---

### アプリ初期化方法

test_013_appinit.py

```python
from libcore_hng.utils.app_core import AppInitializer
from test_013_config import DerivedConfig

class DerivedAppInitializer(AppInitializer[DerivedConfig]):
    """
    AppInitializer拡張クラス
    """
    def __init__(self, base_file: str = __file__, *config_file: str):
        # 基底コンストラクタに拡張Configクラスを渡す
        super().__init__(DerivedConfig, base_file, *config_file)

ins: DerivedAppInitializer | None = None
""" AppInitializer拡張クラスインスタンス """

def init_app(base_file: str = __file__, *config_file: str) -> DerivedAppInitializer:
    """
    アプリケーション初期化
    """
    global ins
    ins = DerivedAppInitializer(base_file, *config_file)
    return ins

```

test_013_config.py

```python
from pydantic import BaseModel
from libcore_hng.core.base_config import BaseConfig
from libcore_hng.utils.app_logger_mixin import LoggingMixin

class Test(BaseModel, LoggingMixin):
    """
    テスト設定クラスモデル
    """

    append_member: str = "A"
    """ 追加メンバー """

class DerivedConfig(BaseConfig):
    """
    BaseConfig拡張クラス
    """
    
    test: Test = Test()
    """ テスト設定クラス """

    @classmethod
    def load_config(cls, base_file, *config_file) -> "DerivedConfig":
        """
        BaseConfigのload_configをoverrride
        戻り値の型は自身とする
        """

        # 基底側のload_configを実行してjsonファイルを読み込む
        base = super().load_config(base_file, *config_file)
        
        # BaseConfigのインスタンスが持つ属性を取り出してDerivedConfigのインスタンスを返す
        # **はキーワード引数に展開する構文(属性をclsに引数渡しする)
        return cls(**base.__dict__)

```

test_013.py

```python
import test_013_appinit as app
import test_013_sub as t013

# アプリ初期化（最初の一度だけ呼び出す）
app.init_app(__file__, "app_config.json")

# 別ファイルのメソッド
t013.test013()

```

test_013_sub.py

```python
import test_013_appinit as app

def test013():
    # 拡張Configクラスのメンバーをprint
    print(app.ins.config.test.append_member)

```

---

### 設定ファイルの暗号化と復号鍵の管理

機密情報を含む設定ファイルを保護するため、ファイルを暗号化し、その復号鍵を Google Cloud Secret Manager に安全に保存して管理します。開発環境と本番環境で同じ仕組みを使用することで、セキュアで統一された運用が可能です。

#### 手順

1. **設定ファイルの暗号化**: `libcore_hng.utils.crypto.create_encryption_file` を使用して、既存のJSONファイルを暗号化します。これにより、元のファイル名に `.enc` が付いた暗号化ファイルが生成され、標準出力に復号鍵が表示されます。
2. **復号鍵の登録**: コンソールに表示された鍵をコピーし、GCP Secret Manager に登録します（例: `my-app-secret-dev`, `my-app-secret-prod`）。

#### 実装例 (`tests/test_016_enc_file.py`)

```python
import libcore_hng.utils.app_core as app
import libcore_hng.utils.crypto as crypto
from libcore_hng.core.base_config import BaseConfig

# アプリ初期化
app.init_app(BaseConfig, __file__, "logger.json")

# 設定ファイルを暗号化して新規ファイル (.enc) として作成
# 戻り値として復号鍵が得られます
key = crypto.create_encryption_file("configs/test-config.json")

# 生成された鍵を表示
print("以下の鍵を GCP Secret Manager に登録してください:")
print(key.decode("utf-8"))
```

`BaseConfig.load_config` は拡張子が `.enc` のファイルを自動的に検知し、暗号化ファイルとして復号・ロードする機能を備えています。

復号に必要なGCP設定は、以下の環境変数、または`app_config.json`で設定された値から自動的に取得されます。

- `GCP_PROJECT_ID`: GCPのプロジェクトID。WIF無効時に使用。
- `GCP_SECRET_NAME`: GCP Secret Manager に登録したシークレットのベース名。WIF無効時に使用。
- `APP_ENV`: 環境名（例: `dev`, `prod`）。シークレット名のサフィックスとして使用されます（デフォルト: `dev`）。

### GCP Workload Identity Federation (WIF) を利用した鍵の取得

`libcore-hng` は、GCP Workload Identity Federation (WIF) を利用して Google Secret Manager から復号鍵を安全に取得する機能をサポートしています。これにより、CI/CD環境や異なるクラウドプロバイダーなど、GCP外の環境から直接サービスアカウントキーを配布することなく、GCPリソースにセキュアにアクセスできます。

#### 仕組み

`secret_manager.py` 内の `_get_secret_with_wif` 関数がこのプロセスを管理します。主な流れは以下の通りです。

1. **自前JWT (Subject Token) の生成**: `libcore-hng` は、設定された発行者 (`issuer`) と秘密鍵 (`WIF_PRIVATE_KEY_PATH` 環境変数またはデフォルトパスから取得) を使用して、自身の認証情報を示す JWT を生成します。この JWT は、WIF プールとプロバイダーをオーディエンスとして指定します。
2. **Google STS (Security Token Service) との連携**: 生成された自前 JWT は、Google STS エンドポイントに送信されます。STS はこの JWT を検証し、GCP が信頼する一時的なフェデレーテッドトークンに交換します。
3. **サービスアカウントの偽装 (Impersonation)**: フェデレーテッドトークンを使用して、指定されたサービスアカウント (`service_account_email`) を偽装するためのアクセスキーを IAM Credentials API から取得します。これにより、`libcore-hng` はそのサービスアカウントが持つ権限で GCP リソースにアクセスできるようになります。
4. **Secret Manager からシークレットを取得**: サービスアカウントとして取得した最終的なアクセスキーを用いて、Google Secret Manager クライアントを初期化し、指定されたシークレット (`secret_name` と `app_env` から構成される) から復号鍵を取得します。

#### 必要な設定

WIF を利用するには、`app_config.json` の `gcp` セクションで以下の設定を行うか、対応する環境変数を設定する必要があります。

- `wif_enabled`: `true` に設定して WIF を有効にします。
- `project_number`: Workload Identity Pool が属する GCP プロジェクトの番号。
- `pool_id`: Workload Identity Pool の ID。
- `provider_id`: Workload Identity Provider の ID。
- `service_account_email`: 偽装する GCP サービスアカウントのメールアドレス。
- `issuer`: 自前 JWT の発行者。通常は WIF プロバイダーの設定と一致させます。
- `kid`: 自前 JWT の署名に使用するキーID。
- `sts_url`: Security Token Service (STS) のエンドポイントURL。デフォルト値が設定されています。
- `iam_credentials_url_base`: IAM Credentials API のベースURL。デフォルト値が設定されています。

また、自前 JWT の署名に使用する秘密鍵のパスを環境変数 `WIF_PRIVATE_KEY_PATH` で指定する必要があります（例: `/path/to/your/private_key.pem`）。指定がない場合は、デフォルトで `~/.ssh/uw_private_key.pem` が使用されます。

※ 例: `GCP_SECRET_NAME=my-app-secret`, `APP_ENV=prod` の場合、GCPから `my-app-secret-prod` のシークレットを取得します。WIF を使用する場合、`GCP_PROJECT_ID` と `GCP_SECRET_NAME` は WIF 無効時のフォールバックとしてのみ機能します。

---

### 環境変数設定例（Docker/ローカル開発）

環境変数を使用して、GCP Secret Manager へのアクセス情報、WIF 関連の設定、またはCI/CD・ローカル用の一時的な復号鍵を直接渡すことができます。`app_config.json` での設定値よりも環境変数が優先されます。

`docker-compose.yml` での設定例を以下に示します。

```yaml
services:
  app:
    image: your-app-image
    environment:
      # --- GCP Workload Identity Federation (WIF) を利用する場合 ---
      - WIF_ENABLED=true
      - GCP_PROJECT_NUMBER=${GCP_PROJECT_NUMBER}
      - GCP_POOL_ID=${GCP_POOL_ID}
      - GCP_PROVIDER_ID=${GCP_PROVIDER_ID}
      - GCP_SERVICE_ACCOUNT_EMAIL=${GCP_SERVICE_ACCOUNT_EMAIL}
      - GCP_ISSUER=${GCP_ISSUER}
      - GCP_KID=${GCP_KID}
      - WIF_PRIVATE_KEY_PATH=/path/to/your/private_key.pem
      - APP_ENV=prod  # 開発時は dev などを指定

      # --- または、従来の GCP Secret Manager 連携 (WIF無効時) ---
      # WIF_ENABLED を false にするか、未設定の場合に適用されます。
      - GCP_PROJECT_ID=${GCP_PROJECT_ID}
      - GCP_SECRET_NAME=${GCP_SECRET_NAME}
      # - APP_ENV=prod は WIF の場合と共通
      
      # --- または、復号鍵を直接指定する場合 (GCP設定より優先されます) ---
      - APP_SECRET_KEY=${APP_SECRET_KEY}
```

※ 開発時やデプロイ時には、Docker Composeが読み込む `.env` ファイルなどにこれらの変数を記述しておくことで、安全に鍵情報や設定をコンテナへ渡すことができます。

---

### `.clinerules` ファイルの取得方法

本リポジトリで一元管理している `.clinerules` ファイルは、以下のコマンドで取得できます。

```bash
curl.exe -L -o .clinerules https://raw.githubusercontent.com/kaioman/libcore-hng/main/.clinerules
```
