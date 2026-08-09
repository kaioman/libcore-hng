from libcore_hng.core.base_config import BaseConfig

class ExtendedExtraConfig(BaseConfig):
    append_member: str = "default"
    dammy_key: str = "default"
    dammy_key1: str = "default"
    dammy_key2: str = "default"
    dammy_key3: str = "default"

class ExtendedConfig(BaseConfig):
    test1: ExtendedExtraConfig = ExtendedExtraConfig()
    test2: ExtendedExtraConfig = ExtendedExtraConfig()
