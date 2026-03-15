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
app.init_app(__file__, "logger.json")

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

復号に必要なGCP設定は、以下の環境変数から自動的に取得されます。

- `GCP_PROJECT_ID`: GCPのプロジェクトID
- `GCP_SECRET_NAME`: GCP Secret Manager に登録したシークレットのベース名
- `APP_ENV`: 環境名（例: `dev`, `prod`）。シークレット名のサフィックスとして使用されます（デフォルト: `dev`）

※ 例: `GCP_SECRET_NAME=my-app-secret`, `APP_ENV=prod` の場合、GCPから `my-app-secret-prod` のシークレットを取得します。

---

### 環境変数設定例（Docker/ローカル開発）

環境変数を使用して、GCP Secret Manager へのアクセス情報や、CI/CD・ローカル用の一時的な復号鍵を直接渡すことができます。

`docker-compose.yml` での設定例を以下に示します。

```yaml
services:
  app:
    image: your-app-image
    environment:
      # GCP Secret Manager を利用する場合
      - GCP_PROJECT_ID=${GCP_PROJECT_ID}
      - GCP_SECRET_NAME=${GCP_SECRET_NAME}
      - APP_ENV=prod  # 開発時は dev などを指定
      
      # --- または ---
      # 復号鍵を直接指定する場合 (GCP設定より優先されます)
      - APP_SECRET_KEY=${APP_SECRET_KEY}
```

※ 開発時やデプロイ時には、Docker Composeが読み込む `.env` ファイルなどにこれらの変数を記述しておくことで、安全に鍵情報や設定をコンテナへ渡すことができます。
