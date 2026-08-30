from pydantic import Field
from libcore_hng.core.base_config_model import BaseConfigModel

class RunPodConfig(BaseConfigModel):
    """
    RunPodManagerの設定クラス
    """

    api_key: str = Field(default="", description="RunPodで発行したAPIキー")
    """ APIキー """
