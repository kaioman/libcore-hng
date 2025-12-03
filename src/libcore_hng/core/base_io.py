import os
import pandas as pd
import libcore_hng.utils.app_core as uwc
from abc import ABC, abstractmethod
from libcore_hng.exceptions.directory_exception import DirectoryNotFoundError

class BaseIO(ABC):
    """
    インポート/エクスポート基底クラス
    """

    def exists_directory(self, output_dir):
        """
        ディレクトリ存在確認

        Parameters
        ----------
        output_dir : str
            ディレクトリ
        """
        
        # ディレクトリ存在確認
        if not os.path.isdir(output_dir):
            raise DirectoryNotFoundError(output_dir)

    def get_fullpath(self, output_dir, filename) -> str:
        """
        フルパスを取得する

        Parameters
        ----------
        output_dir : str
            ディレクトリ
        filename : str
            ファイル名
        """

        # output_dirが相対パスか絶対パス判定してフルパスを取得する
        if os.path.isabs(output_dir):
            return os.path.join(output_dir, filename)
        else:
            return os.path.join(uwc.core.config.project_root_path, output_dir, filename)
        
class BaseImporter(BaseIO):
    """
    インポート基底クラス
    """
    
    @abstractmethod
    def to_dataframe(self, *args, **kwargs):
        """
        ファイル等からデータを読み込む抽象メソッド
        """
        raise NotImplementedError
    
class BaseExporter(BaseIO):
    """
    エクスポート基底クラス
    """
    
    @abstractmethod
    def save(self, *args, **kwargs):
        """
        ファイル等へデータを書き込む抽象メソッド
        """
        raise NotImplementedError

    def fillna_dataframe(self, df:pd.DataFrame):
        """
        DataFrameの欠損値置換
        
        Parameters
        ----------
        df : DataFrame
            fillnaを実行するDataFrame
        """
        
        return df.fillna('')