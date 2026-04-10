from pydantic import Field
from libcore_hng.core.base_config_model import BaseConfigModel

class AddConfig(BaseConfigModel):
    
    path1 : str = Field(default="")
    path2 : str = Field(default="")
    path3 : str = Field(default="")

