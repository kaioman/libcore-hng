from libcore_hng.core.base_app_exception import AppBaseException

class OutputDirectoryNotFoundError(AppBaseException):
    """
    独自例外クラス(出力先ディレクトリ例外)
    
    - ファイル保存処理などで指定された出力先ディレクトリが存在しない場合に発生する
    """

    def __init__(self, directory: str):
        """
        Parameters
        ----------
        directory : str
            存在しないと判定されたディレクトリのパス
        """

        self.directory = directory
        super().__init__(f"出力先ディレクトリが存在しません: {directory}")
