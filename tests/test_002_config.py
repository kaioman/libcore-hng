from libcore_hng.core.base_config import BaseConfig
from pydantic import BaseModel

class Test(BaseModel):

    append_member: str = "A"
    """ 追加メンバー """

class DerivedConfig(BaseConfig):
    test: Test = Test()

cfg: DerivedConfig | None = None
