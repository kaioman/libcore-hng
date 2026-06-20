from dataclasses import dataclass
from typing import Any, Dict, Optional

@dataclass
class PodStatus:
    """
    RunPodインスタンスのステータス及び変更履歴を保持するデータクラス
    """
    
    status: str
    """
    Podの状態(例: RUNNING, EXITED, TREMINATED)
    """

    reason: Optional[str] = None
    """
    ステータスが変更された理由、詳細メッセージ
    """
    
    started_at: Optional[str] = None
    """
    RunPodが最後に起動した日時(UTC)
    """

    extra: Dict[str, Any] = None
    """
    基本項目に含まれないその他のステータス関連メタデータ
    """

@dataclass
class PodInfo:
    """
    RunPodインスタンスの全体情報を内包するデータクラス
    """

    id: str
    """
    Podのユニークな識別子
    """

    name: Optional[str]
    """
    ユーザーが設定した、または自動生成されたPodの表示名
    """

    status: PodStatus
    """
    Podの稼働状態や起動日時などを格納したPodStatusオブジェクト
    """

    spec: Dict[str, Any]
    """
    Podに割り当てられているハードウェアスペック(CPU,メモリ,ディスクなど)の辞書
    """

    raw: Dict[str, Any]
    """
    RunPod APIから直接返却された加工前の生JSONデータ
    """
