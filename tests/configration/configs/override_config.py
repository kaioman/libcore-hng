from libcore_hng.core.base_config import BaseConfig
from libcore_hng.configs.logger import LoggerConfig

class OverrideLoggerConfig(LoggerConfig):
    ext1: str = "default"

class OverrideAppConfig(BaseConfig):
    logging: OverrideLoggerConfig = OverrideLoggerConfig()