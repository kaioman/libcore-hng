import pandas as pd
from abc import ABC, abstractmethod

class BaseImporter(ABC):
    """
    インポート基底クラス
    """
    
    @abstractmethod
    def load(self, *args, **kwargs):
        """
        ファイル等からデータを読み込む抽象メソッド
        """
        raise NotImplementedError
    
class BaseExporter(ABC):
    """
    エクスポート基底クラス
    """
    
    @abstractmethod
    def save(self, *args, **kwargs):
        """
        ファイル等へデータを書き込む抽象メソッド
        """
        raise NotImplementedError

    def fillnaDataFrame(self, df:pd.DataFrame):
        """
        DataFrameの欠損値置換
        
        Parameters
        ----------
        df : DataFrame
            fillnaを実行するDataFrame
        """
        
        return df.fillna('')