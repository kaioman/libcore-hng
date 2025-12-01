from libcore_hng.core.base_app_exception import AppBaseException

class FileNotFoundErrorEx(AppBaseException):
    """
    ファイル例外クラス(汎用)
    
    - ファイル読込処理などで指定されたファイルが存在しない場合に発生する
    - 標準のFileNotFoundErrorと名前衝突しないよう命名
    """

    def __init__(self, file_path: str):
        """
        Parameters
        ----------
        file_path : str
            存在しないと判定されたファイルパス
        """

        self.file_path = file_path
        super().__init__(f"ファイルが存在しません: {file_path}")

class ImageFileNotFoundError(AppBaseException):
    """
    画像ファイル例外クラス
    
    - 画像ファイルが存在しない場合に発生する
    """

    def __init__(self, file_path: str):
        """
        Parameters
        ----------
        file_path : str
            存在しないと判定されたファイルパス
        """

        self.file_path = file_path
        super().__init__(f"画像ファイルが存在しません: {file_path}")

class FontFileNotFoundError(AppBaseException):
    """
    フォントファイル例外クラス
    
    - フォントファイルが存在しない場合に発生する
    """

    def __init__(self, file_path: str):
        """
        Parameters
        ----------
        file_path : str
            存在しないと判定されたファイルパス
        """

        self.file_path = file_path
        super().__init__(f"フォントファイルが存在しません: {file_path}")
