import test_023_config
from libcore_hng.utils.app_core import AppInitializer

class TestAppInitializer(AppInitializer[test_023_config.EncTestConfig]):
    """
    AppInitializer拡張クラス
    """
    def __init__(self, base_file: str = __file__, *config_file: str):
        # 基底コンストラクタに拡張Configクラスを渡す
        super().__init__(test_023_config.EncTestConfig, base_file, *config_file)

core: TestAppInitializer | None = None
""" AppInitializer拡張クラスインスタンス """

def init_app(base_file: str = __file__, *config_file: str) -> TestAppInitializer:
    """
    アプリケーション初期化
    """
    global core
    core = TestAppInitializer(base_file, *config_file)
    return core
