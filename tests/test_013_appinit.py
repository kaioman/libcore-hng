from libcore_hng.utils.app_core import AppInitializer
from test_013_config import DerivedConfig

class DerivedAppInitializer(AppInitializer[DerivedConfig]):
    """
    AppInitializer拡張クラス
    """
    def __init__(self, base_file: str = __file__, *config_file: str):
        # 基底コンストラクタに拡張Configクラスを渡す
        super().__init__(DerivedConfig, base_file, *config_file)

core: DerivedAppInitializer | None = None
""" AppInitializer拡張クラスインスタンス """

def init_app(base_file: str = __file__, *config_file: str) -> DerivedAppInitializer:
    """
    アプリケーション初期化
    """
    global core
    core = DerivedAppInitializer(base_file, *config_file)
    return core
