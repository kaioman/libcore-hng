import libcore_hng.core.base_config as bcfg
import libcore_hng.utils.app_logger as app_logger
from libcore_hng.exceptions import ConfigurationException 

def some_proccess():
    try:
        1 / 0
    except ZeroDivisionError as e:
        raise ConfigurationException(e)

# 共通設定クラスインスタンス生成
bcfg.cfg = bcfg.BaseConfig.load_config(
    __file__,
    "logger.json"
)

# ロガー設定
app_logger.setting(bcfg.cfg)

try:
    some_proccess()
except ConfigurationException as e:
    print(f"Caught on exception: {e}")
    
app_logger.info("Test Info message")
app_logger.warning("Test Warning message")
