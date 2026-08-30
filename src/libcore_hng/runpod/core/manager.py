from abc import ABC, abstractmethod
from typing import Dict, Any
from libcore_hng.runpod.models import PodInfo, PodStatus

class PodManager(ABC):
    """
    RunPodマネージャーの抽象インターフェース
    """

    @abstractmethod
    def deploy(self, spec: Dict[str, Any]) -> PodInfo:
        """
        新しいPod(インスタンス)を新規作成・デプロイする

        Parameters
        ----------
        spce : Dict[str, Any]
            作成するPodの構成情報（Dockerイメージ名、GPUタイプ、環境変数など)

        Returns
        -------
            PodInfo : ステータスやスペック構造を含むPod情報オブジェクト

        """
        pass

    @abstractmethod
    def start(self, pod_id: str) -> PodInfo:
        """
        停止中のPodを開始する

        Parameters
        ----------
        pod_id : str
            起動対象のPod ID

        Returns
        -------
            PodInfo : ステータスやスペック構造を含むPod情報オブジェクト

        """
        pass

    @abstractmethod
    def stop(self, pod_id: str) -> PodInfo:
        """
        実行中のPodを停止する

        Parameters
        ----------
        pod_id : str
            停止対象のPod ID

        Returns
        -------
            PodInfo : ステータスやスペック構造を含むPod情報オブジェクト
        
        """
        pass

    @abstractmethod
    def terminate(self, pod_id: str) -> PodInfo:
        """
        Podを削除する

        Parameters
        ----------
        pod_id : str
            削除対象のPod ID

        Returns
        -------
            PodInfo : ステータスやスペック構造を含むPod情報オブジェクト
        
        """
        pass

    @abstractmethod
    def get_status(self, pod_id: str) -> PodInfo:
        """
        Pod情報を取得する

        Parameters
        ----------
        pod_id : str
            取得対象のPod ID

        Returns
        -------
            PodInfo : ステータスやスペック構造を含むPod情報オブジェクト        
        """
        pass

