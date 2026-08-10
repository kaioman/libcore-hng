import json
from pathlib import Path
from dataclasses import asdict
from libcore_hng.core.base_config import BaseConfig
from libcore_hng.utils.app_core import AppInitializer
from libcore_hng.runpod.models.config import RunPodConfig
from libcore_hng.runpod.pod_manager import RunPodManager

class RunPodMainConfig(BaseConfig):
    runpod: RunPodConfig = RunPodConfig()
    
class PodAppInitializer(AppInitializer[RunPodMainConfig]):
    """
    AppInitializer拡張クラス
    """
    def __init__(self, base_file: str = __file__, *config_file: str):
        # 基底コンストラクタに拡張Configクラスを渡す
        super().__init__(RunPodMainConfig, base_file, *config_file)

def init_app(base_file: str = __file__, *config_file: str) -> PodAppInitializer:
    """
    アプリケーション初期化
    """
    return PodAppInitializer(base_file, *config_file)

def main():

    # 1. spceJSON取得
    BASE_DIR = Path(__file__).resolve().parent
    json_path = BASE_DIR / "spec_json" / "pod_cpu_worker_spec.json"
    with open(json_path, "r", encoding="utf-8") as f:        
        default_spec = json.load(f)

    # 2. アプリ・Podマネージャー初期化
    pod_name = "personyx_runpod_environment"
    app = init_app(__file__, "app_config.json", "gcp_config.json", "pod-config.json.enc")
    mgr = RunPodManager(app.config.runpod.api_key)

    # 3. Pod起動(失敗時はdeploy)
    try:
        pdinfo = mgr.start_by_name_or_recreate(pod_name, default_spec)
    except Exception as e:
        print(f"pod request error {e}")
        return

    # 4. status出力
    pdinfo_dict = asdict(pdinfo)
    print(json.dumps(pdinfo_dict, indent=4, ensure_ascii=False))

if __name__ == "__main__":
    main()