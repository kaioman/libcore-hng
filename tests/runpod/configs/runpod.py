from libcore_hng.core.base_config import BaseConfig
from libcore_hng.runpod.models.config import RunPodConfig
from pydantic import Field

class RunPodConfigExt(RunPodConfig):
    ext: str = Field(default="", description="RunPod設定拡張項目")

class RunPodOverrideConfig(BaseConfig):
    runpod: RunPodConfig = RunPodConfigExt()
    
