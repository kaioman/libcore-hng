from libcore_hng.core.app_base_exception import AppBaseException

class ConfigurationException(AppBaseException):
    """
    独自例外クラス(設定例外)
    
    - 設定関連の例外階層の基底クラス
    - AppBaseExceptionを継承し、設定固有の例外処理を追加する場合に使用
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