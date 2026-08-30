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
