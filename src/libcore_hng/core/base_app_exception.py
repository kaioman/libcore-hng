import traceback
import uuid
import libcore_hng.utils.app_logger as app_logger

class AppBaseException(Exception):
    
    """
    独自例外クラス(基底)
    
    - プロジェクト固有の例外階層の基底クラス
    - 捕捉した例外をラップし、UUIDを付与してログやデバッグを容易にする
    """
    
    def __init__(self, exc: Exception = None):
        
        """
        コンストラクタ
        
        Parameters
        ----------
        exc : Exception, optional
            捕捉した例外オブジェクト。指定しない場合は None。
            渡された例外の型・値・トレースバックを保持する。
        """
        
        super().__init__(str(exc) if exc else "")
        
        # 例外情報取得
        if isinstance(exc, BaseException):
            # Exceptionオブジェクトをラップする
            self._exc_type = type(exc) if exc else None
            self._exc_value = exc
            self._exc_traceback = (
                ''.join(traceback.format_exception(type(exc), exc, exc.__traceback__))
                if exc else None
            )
        elif isinstance(exc, str):
            # メッセージ文字列のみ保持する
            self._exc_type = None
            self._exc_value = exc
            self._exc_traceback = None
        else:
            # 例外なしの場合
            self._exc_type = None
            self._exc_value = None
            self._exc_traceback = None
            
        self._exc_uuid = str(uuid.uuid4())

        # ログ出力
        self.log()
        
    @property
    def exc_type(self):
        """
        捕捉した例外の型（例: ValueError）。未指定の場合は None
        """
        return self._exc_type

    @property
    def exc_value(self):
        """
        捕捉した例外オブジェクトそのもの。未指定の場合は None
        """
        return self._exc_value

    @property
    def exc_traceback(self):
        """
        捕捉した例外のトレースバック文字列。未指定の場合は None
        """
        return self._exc_traceback

    @property
    def exc_uuid(self):
        """
        例外インスタンスごとに付与される一意の識別子
        """
        return self._exc_uuid

    def __str__(self):
        """
        例外の文字列表現。

        - UUID, 型名, 値, トレースバックを含む
        - 捕捉例外がない場合は UUID のみを返す
        """
        if self._exc_type:
            return (f"[{self._exc_uuid}] {self._exc_type.__name__}: {self._exc_value}\n"
                    f"{self._exc_traceback}")
        return f"[{self._exc_uuid}] No exception captured."
    
    def __repr__(self):
        """
        デバッグ用の簡易表現
        UUID・型・値を含む
        """
        return f"<AppBaseException uuid={self._exc_uuid} type={self._exc_type} value={self._exc_value}>"
    
    def log(self):
        """
        例外情報をログに出力する

        - UUID, 型名, 値, トレースバックをログに記録
        """
        if self._exc_type:
            app_logger.error(f"Exception [{self._exc_uuid}]: {self._exc_type.__name__}: {self._exc_value}")
            app_logger.error(f"Traceback:\n{self._exc_traceback}")
        elif self._exc_value:
            app_logger.error(f"Exception [{self._exc_uuid}]: Message: {self._exc_value}")
        else:
            app_logger.error(f"Exception [{self._exc_uuid}]: No exception captured.")