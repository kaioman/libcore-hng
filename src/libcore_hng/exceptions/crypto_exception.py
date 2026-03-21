from libcore_hng.core.base_app_exception import AppBaseException

class CryptoException(AppBaseException):
    """
    暗号処理例外クラス
    
    - 暗号化関連の例外階層の基底クラス
    - AppBaseExceptionを継承し、暗号化・復号化固有の例外処理を追加する場合に使用
    """
    
    def __init__(self, exc: Exception = None):
        """
        コンストラクタ
        
        Parameters
        ----------
        exc : Exception, optional
            捕捉した例外オブジェクト。指定しない場合は None
            渡された例外の型・値・トレースバックを保持する
        """
        super().__init__(exc)
