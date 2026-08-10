import os
import pytest
import json
from pathlib import Path
from dataclasses import asdict
from tenacity import retry, stop_after_delay, wait_fixed, retry_if_result
from libcore_hng.runpod.pod_manager import RunPodManager
from custum_app_init.app_init import config

class TestRunpodManager:
    """
    RunPod操作テスト

    実行コマンド例：
    cpu
        pytest -sv tests/runpod/test_pod_manage.py --pod-name=personyx_runpod_environment
    gpu
        pytest -sv tests/runpod/test_pod_manage.py --pod-name=personyx_runpod --machine-type=gpu

    デバッグ実行時は環境変数 SKIP_STOP_TEST にtrueをセットし、stopテストをスキップするため
    デバッグ確認後はRunpodを停止することを忘れないよう注意
    """

    @pytest.fixture(autouse=True)
    def setup(self, pod_name, machine_type):

        # Pod名設定
        self.pod_name = pod_name
        # マシンタイプ設定
        self.machine_type = machine_type
        # デフォルトspec取得
        self.spec = self.get_spec(machine_type)
        # アプリ・Podマネージャー初期化
        self.mgr = RunPodManager(config.runpod.api_key)

    def get_spec(self, machine_type):

        # spceJSON取得
        BASE_DIR = Path(__file__).resolve().parent
        json_path = BASE_DIR / "spec_json" / f"pod_{machine_type}_worker_spec.json"

        if not json_path.exists():
            raise FileNotFoundError(f"specファイルが存在しません: {json_path}")

        with open(json_path, "r", encoding="utf-8") as f:        
            default_spec = json.load(f)

        return default_spec

    @staticmethod
    def _is_not_exited(pdinfo) -> bool:
        status = asdict(pdinfo).get("status", {}).get("status")
        return status != "EXITED"

    @retry(
        stop=stop_after_delay(60),
        wait=wait_fixed(3),
        retry=retry_if_result(_is_not_exited),
        reraise=True
    )
    def wait_for_exit(self, pod_id: str):
        print("ステータス確認中...")
        pdinfo = self.mgr.get_status(pod_id)        
        pdinfo_dict = asdict(pdinfo)
        print(json.dumps(pdinfo_dict, indent=4, ensure_ascii=False))
        return pdinfo

    @pytest.mark.order(1)
    def test_runpod_get_status(self):

        # 1. PodInfo取得
        pi = self.mgr.find_by_name(self.pod_name)

        # 2. get_status実行
        pdinfo = self.mgr.get_status(pi.id)

        # 3. status出力
        pdinfo_dict = asdict(pdinfo)
        print(json.dumps(pdinfo_dict, indent=4, ensure_ascii=False))

        # 検証
        assert pdinfo_dict.get("name") == self.pod_name
        assert pdinfo_dict.get("status", {}).get("status") == "EXITED"

    @pytest.mark.order(2)
    def test_runpod_start_or_recreate(self):

        # 1. start実行
        pdinfo = self.mgr.start_by_name_or_recreate(self.pod_name, self.spec)

        # 2. status出力
        pdinfo_dict = asdict(pdinfo)
        print(json.dumps(pdinfo_dict, indent=4, ensure_ascii=False))

        # 検証
        assert pdinfo_dict.get("name") == self.pod_name
        assert pdinfo_dict.get("status", {}).get("status") == "RUNNING"

    @pytest.mark.skipif(
        os.getenv("SKIP_STOP_TEST", "false") == "true",
        reason="環境変数により停止テストをスキップします"
    )
    @pytest.mark.order(-1)
    def test_runpod_stop(self):

        # 1. PodInfo取得
        pi = self.mgr.find_by_name(self.pod_name)

        # 2. stop実行
        self.mgr.stop(pi.id)

        # 3. stop後の監視
        final_pdinfo = self.wait_for_exit(pi.id)
        final_pdinfo_dict = asdict(final_pdinfo)

        # 4. status取得
        final_status = final_pdinfo_dict.get("status", {}).get("status")

        # 検証
        assert final_pdinfo_dict.get("name") == self.pod_name
        assert final_status == "EXITED"

if __name__ == "__main__":
    os.environ["SKIP_STOP_TEST"] = "true"
    pytest.main(["-s", "-v", __file__, "--pod-name=personyx_runpod_environment"])
