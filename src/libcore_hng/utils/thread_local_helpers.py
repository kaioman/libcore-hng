import threading

class ThreadLocalDepth(threading.local):
    """
    スレッドローカルでネストの深さを管理するクラス
    """
    
    depth: int = 0
    """ スレッドの深さ """