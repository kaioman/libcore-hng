import json
from dataclasses import asdict
from libcore_hng.core.base_config import BaseConfig
from libcore_hng.utils.app_core import AppInitializer
from libcore_hng.runpod.models.config import RunPodConfig
from libcore_hng.runpod.pod_manager import RunPodManager
from pydantic import Field

class RunPodConfigExt(RunPodConfig):
    ext: str = Field(default="", description="RunPod設定拡張項目")

class RunPodMainConfig(BaseConfig):
    runpod: RunPodConfig = RunPodConfigExt()
    
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
    pod_id = "70kpwz8avp3vm0"

    # 1. 実行する操作を選択
    print("----------------------------------------")
    print("実行する操作を選択してください:")
    print("  1: get_status")
    print("  2: start")
    print("  3: stop")
    print("----------------------------------------")

    user_input = input("番号またはメソッド名を入力してください [1/2/3]:").strip().lower()

    # 入力のマッピング
    method_map = {
        "1": "get_status", "get_status": "get_status",
        "2": "start", "start": "start",
        "3": "stop", "stop": "stop",                        
    }
    method = method_map.get(user_input)
    if not method:
        print(f"[エラー] 不正な入力です: '{user_input} (1, 2, 3 またはメソッド名を指定してください)")
        return

    # 2. アプリ・Podマネージャー初期化
    app = init_app(__file__, "app_config.json", "gcp_config.json", "pod-config.json.enc", "run_pod_config.json")
    mgr = RunPodManager(app.config.runpod.api_key)

    # 3. 引数に応じたメソッド実行
    if hasattr(mgr, method):
        action = getattr(mgr, method)
        pdinfo = action(pod_id)
    else:
        raise ValueError(f"Unknown method: {method}")

    # 4. status出力
    pdinfo_dict = asdict(pdinfo)
    print(json.dumps(pdinfo_dict, indent=4, ensure_ascii=False))

if __name__ == "__main__":
    main()