from pydantic import BaseModel
from libcore_hng.core.base_config import BaseConfig
from libcore_hng.utils.app_logger_mixin import LoggingMixin
class Test(BaseModel, LoggingMixin):

    append_member: str = "A"
    """ 追加メンバー """

    def log_test(self):
        print("Logging from Test class")
        
class DerivedConfig(BaseConfig):
    test: Test = Test()

cfg: DerivedConfig | None = None
