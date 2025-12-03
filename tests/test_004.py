import libcore_hng.utils.app_core as app
import libcore_hng.utils.app_logger as app_logger
from libcore_hng.exceptions import ConfigurationException 
from libcore_hng.core.base_config import BaseConfig

def some_proccess():
    try:
        1 / 0
    except ZeroDivisionError as e:
        raise ConfigurationException(e)

# アプリ初期化
app.init_app(BaseConfig, __file__, "logger.json")

try:
    some_proccess()
except ConfigurationException as e:
    print(f"Caught on exception: {e}")
    
app_logger.info("Test Info message")
app_logger.warning("Test Warning message")
