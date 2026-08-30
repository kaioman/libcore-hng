import libcore_hng.utils.app_logger as app_logger
from pydantic import BaseModel
from libcore_hng.core.base_config import BaseConfig
from libcore_hng.utils.app_logger_mixin import LoggingMixin

class Test(BaseModel, LoggingMixin):

    dammy_key: str = "A"
    """ ダミーキー """

    dammy_key3: str = "C"
    """ ダミーキー3 """
    
class Test2(BaseModel, LoggingMixin):
    
    dammy_key2: str = "B"
    """ ダミーキー2 """

class EncTestConfig(BaseConfig):
    test: Test = Test()
    test2: Test2 = Test2()

    @classmethod
    def load_config(cls, base_file, *config_file) -> "EncTestConfig":
        base = super().load_config(base_file, *config_file)
        return cls(**base.__dict__)

cfg: EncTestConfig | None = None
