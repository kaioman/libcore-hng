import libcore_hng.utils.app_logger as app_logger
from pydantic import BaseModel
from libcore_hng.core.base_config import BaseConfig
from libcore_hng.utils.app_logger_mixin import LoggingMixin
class Test(BaseModel, LoggingMixin):

    append_member: str = "A"
    """ 追加メンバー """
    
    def log_test(self):
        app_logger.info("Logging from Test class")
        self.log_test2()
        
    def log_test2(self):
        app_logger.info("Logging from Test class. depth 2")
class DerivedConfig(BaseConfig):
    test: Test = Test()

    @classmethod
    def load_config(cls, base_file, *config_file) -> "DerivedConfig":
        base = super().load_config(base_file, *config_file)
        return cls(**base.__dict__)

cfg: DerivedConfig | None = None
