import json
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
    pod_id = "7adqlu3bx2zw70"

    # 1. アプリ・Podマネージャー初期化
    app = init_app(__file__, "app_config.json", "gcp_config.json", "pod-config.json.enc")
    mgr = RunPodManager(app.config.runpod.api_key)

    # 2. get_status実行
    pdinfo = mgr.get_status(pod_id)

    # 3. 対象Podのspec取得
    pod_spec = mgr.extract_deploy_spec(pdinfo)

    # 4. pod_specをJSONファイルとして保存
    path = "configs/spec.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(pod_spec, f, indent=4, ensure_ascii=False)

    print(f"Output spec.json. {path}")

if __name__ == "__main__":
    main()