import requests
import time
from typing import Optional, Dict, Any, List
from libcore_hng.runpod.core.manager import PodManager
from libcore_hng.runpod.models import PodInfo, PodStatus

class RunPodManager(PodManager):
    """
    RunPodマネージャークラス
    """

    def __init__(self, api_key: str, base_url: str = "https://rest.runpod.io/v1"):
        """
        コンストラクタ

        Parameters
        ----------
        api_key : str
            APIアクセスキー
        base_url : str
            APIリクエスト先のベースUrl
        
        """
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        })

    def _request(self, method: str, path: str, json: Optional[Dict] = None, retries: int = 2, timeout: int = 10):
        """
        HTTPリクエスト送信メソッド

        Parameters
        ----------
        method : str
            HTTPメソッド(GET, POST, DELETEなど)
        path :  str
            エンドポイントの相対パス(例: '/pods')
        json : Optional[Dict]
            リクエストボディに含めるJSONデータ
        retries : int
            最大再試行回数(デフォルト=2)
        timeout : int
            タイムアウト秒数(デフォルト=10) 

        Returns
        -------
            Dict[str, Any]: APIから返却されたレスポンスのJSONデータ

        Raises
        ------
            requests.RequestException: 既定回数のリトライ後もリクエストが失敗した場合、
            またはHTTPステータスコードがエラー(4xx, 5xx)を示している場合に送出
        """
        url = f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"
        for attempt in range(retries + 1):
            try:
                resp = self.session.request(method, url, json=json, timeout=timeout)
                resp.raise_for_status()

                # 204 No Content
                if resp.status_code == 204:
                    return None

                # JSONレスポンスを返す
                return resp.json()

            except requests.RequestException as exc:
                if exc.response is not None:
                    print("\n[RunPod API Error Response Body]:")
                    print(exc.response.text)
                    print("-" * 40)
                if attempt == retries:
                    raise
                time.sleep(1 + attempt)

    def _to_podinfo(self, raw: Dict[str, Any]) -> PodInfo:
        """
        APIから取得した生JSONデータをアプリケーション共通モデルオブジェクトに変換する

        Parameters
        ----------
        raw : Dict[str, Any]
            RunPod APIから返却された加工前の生レスポンスDict
        
        Returns
        -------
            PodInfo : ステータスやスペック構造を含むPod情報オブジェクト
        """
        # 1.基本情報
        pod_id = raw.get("id")
        name = raw.get("name")

        # 2.マシンスペックに関する項目
        spec_keys = {"vcpuCount", "memoryInGb", "containerDiskInGb", "volumeInGb", "cpuFlavorId", "machine"}
        spec = {k: raw[k] for k in spec_keys if k in raw}

        # 3.状態に関するオブジェクト(PodStatus)
        reserved_keys = {
            "id", "name", "desiredStatus", "lastStartedAt", "lastStatusChange",
            "vcpuCount", "memoryInGb", "containerDiskInGb", "volumeInGb", "cpuFlavorId", "machine"
        }
        extra = {k: v for k, v in raw.items() if k not in reserved_keys}
        
        status = PodStatus(
            status=raw.get("desiredStatus", "unknown"),
            reason=raw.get("lastStatusChange"),
            started_at=raw.get("lastStartedAt"),
            extra=extra
        )

        # PodInfoを返す
        return PodInfo(
            id=str(pod_id),
            name=name,
            status=status,
            spec=spec,
            raw=raw
        )

    def extract_deploy_spec(self, pod_info: PodInfo) -> Dict[str, Any]:
        """
        get_statusで取得した PodInfo から、deploy()に渡す spec 辞書を抽出する

        Parameters
        ----------
        pod_info : PodInfo
            get_statusで取得した PodInfo
        
        Returns
        -------
            Dict[str, Any] : deploy()に渡す spec 辞書
        """

        raw = pod_info.raw
        extra = pod_info.status.extra if pod_info.status else {}
        spec = pod_info.spec or {}

        # deploy 時に RunPodが受け付けるパラメーターのみ抽出する
        deploy_spec = {
            # 基本情報
            "name": pod_info.name,
            "templateId": extra.get("templateId") or raw.get("templateId"),
            "computeType": "CPU",
            "networkVolumeId": extra.get("networkVolumeId") or raw.get("networkVolumeId"),
            "volumeMountPath": extra.get("volumeMountPath") or raw.get("volumeMountPath", "/workspace"),
            "env": extra.get("env") or raw.get("env", {}),
            
            # リソース定義 (CPU / メモリ / Disk)
            "vcpuCount": spec.get("vcpuCount") or raw.get("vcpuCount"),
            "containerDiskInGb": spec.get("containerDiskInGb") or raw.get("containerDiskInGb", 1),
           
            # GPU構成（GPU Podの場合）
            "gpuTypeId": extra.get("gpuTypeId") or raw.get("gpuTypeId"),
            "gpuCount": extra.get("gpuCount") or raw.get("gpuCount"),
        }

        # 値がNoneのキーを除外して整形
        return {
            k: v for k, v in deploy_spec.items() if v is not None
        }

    def list_pods(self) -> List[PodInfo]:
        """
        保有している全Podの一覧を取得する

        Returns
        -------
        List[PodInfo]
            保有するPodのPodInfoオブジェクトリスト
        
        """

        raw_list = self._request("GET", "/pods")
        if isinstance(raw_list, list):
            return [self._to_podinfo(p) for p in raw_list]
        return []

    def find_by_name(self, name: str) -> Optional[PodInfo]:
        """
        指定されたPod名(name)を持つ既存Podを検索する
        最初に見つかったPod名称に対するPodInfoオブジェクトを返す

        Parameters
        ----------
        name : str
            検索対象となるPod名称

        Returns
        -------
        PodInfo
            検索されたPod情報を保持するPodInfoオブジェクト
            
        """

        pods = self.list_pods()
        for pod in pods:
            if pod.name == name:
                return pod
        return None

    def start_by_name_or_recreate(self, name: str, default_spec: Dict[str, Any]) -> PodInfo:
        """
        指定されたPodの名称でPodを起動する。
        - 存在しない場合は default_spec から新規作成(deploy)する
        - 起動に失敗した場合は旧Podを削除し、旧Podと同じ構成で再作成・起動する
        """

        # Pod名からPodIdを取得する
        existing_pod = self.find_by_name(name)

        if existing_pod is not None:
            # 既存Podが存在する場合はStartを試行する
            try:
                print(f"[Info] Starting existing pod `{name}` (ID: {existing_pod.id})...")
                return self.start(existing_pod.id)
            except requests.RequestException as exc:
                print(f"[Warning] Failed to start pod `{name}` (ID: {existing_pod.id}): {exc}")
                print(f"[Info] Terminating degraded pod and recreating...")

                # 起動失敗時のフォールバック処理
                # 既存の構成を抽出（抽出に失敗した場合は default_spec を使用する)
                deploy_spec = self.extract_deploy_spec(existing_pod) or default_spec
                deploy_spec["name"] = name

                # 旧Podを削除する
                try:
                    self.terminate(existing_pod.id)
                except Exception as e:
                    print(f"[Warning] Failed to terminate old pod: {e}")

                # 新Podをデプロイする
                return self.deploy(deploy_spec)
        else:
            # 既存Podが存在しない場合は新規deploy
            print(f"[Info] Pod `{name}` not found. Deploying new pod...")
            spec = default_spec.copy()
            spec["name"] = name
            return self.deploy(spec)
        
    def deploy(self, spec: Dict[str, Any]) -> PodInfo:
        """
        指定されたスペックで新しいPodをデプロイする

        Parameters
        ----------
        spec : Dict[str, Any]
            Podのデプロイ設定
            RunPod APIのCreate Podで受付可能なパラメーターを指定する
        
        Returns
        -------
        PodInfo
            デプロイされたPod情報を保持するPodInfoオブジェクト
        
        Raises
        -------
        requests.RequestException
            APIリクエストに失敗した場合に送出
        """
        raw = self._request("POST", "/pods", json=spec)
        return self._to_podinfo(raw)
    
    def start(self, pod_id: str) -> PodInfo:
        """
        指定されたPodを起動する

        Parameters
        ----------
        pod_id : str
            起動対象のPod ID

        Returns
        -------
        PodInfo
            起動したPod情報を保持するPodInfoオブジェクト
        
        Raises
        -------
        requests.RequestException
            APIリクエストに失敗した場合に送出
        """
        raw = self._request("POST", f"/pods/{pod_id}/start")
        return self._to_podinfo(raw)
    
    def stop(self, pod_id: str) -> PodInfo:
        """
        指定されたPodを停止する

        Parameters
        ----------
        pod_id : str
            停止対象のPod ID

        Returns
        -------
        PodInfo
            停止したPod情報を保持するPodInfoオブジェクト
        
        Raises
        -------
        requests.RequestException
            APIリクエストに失敗した場合に送出
        """
        raw = self._request("POST", f"/pods/{pod_id}/stop")
        return self._to_podinfo(raw)

    def terminate(self, pod_id: str) -> None:
        """
        指定されたPodを削除する


        Parameters
        ----------
        pod_id : str
            削除対象のPod ID

        Returns
        -------
        None
            Podの削除に成功した場合は何も返さない
        
        Raises
        -------
        requests.RequestException
            APIリクエストに失敗した場合に送出
        """
        self._request("DELETE", f"/pods/{pod_id}")

    def get_status(self, pod_id: str) -> PodInfo:
        """
        指定されたPodの状態を取得する


        Parameters
        ----------
        pod_id : str
            状態を取得するPod ID

        Returns
        -------
        PodInfo
            Podの状態及びスペック情報を保持するPodInfoオブジェクト
        
        Raises
        -------
        requests.RequestException
            APIリクエストに失敗した場合に送出
        """
        raw = self._request("GET", f"/pods/{pod_id}")
        return self._to_podinfo(raw)
