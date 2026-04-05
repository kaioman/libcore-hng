import libcore_hng.utils.app_logger as app_logger
from pydantic import BaseModel
from libcore_hng.core.base_config import BaseConfig
from libcore_hng.utils.app_logger_mixin import LoggingMixin

class Test(BaseModel, LoggingMixin):

    dammy_key: str = "A"
    """ ダミーキー """
    
class EncTestConfig(BaseConfig):
    test: Test = Test()

    @classmethod
    def load_config(cls, base_file, *config_file) -> "EncTestConfig":
        base = super().load_config(base_file, *config_file)
        return cls(**base.__dict__)

cfg: EncTestConfig | None = None
