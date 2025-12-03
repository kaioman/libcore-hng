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
