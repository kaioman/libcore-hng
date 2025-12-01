from libcore_hng.core.base_app_exception import AppBaseException

class DirectoryNotFoundError(AppBaseException):
    """
    ディレクトリ例外クラス
    
    - ファイル保存処理などで指定されたディレクトリが存在しない場合に発生する
    """

    def __init__(self, directory: str):
        """
        Parameters
        ----------
        directory : str
            存在しないと判定されたディレクトリのパス
        """

        self.directory = directory
        super().__init__(f"ディレクトリが存在しません: {directory}")
