import os
import pandas as pd
import libcore_hng.core.base_config as bcfg
from libcore_hng.core.base_io import BaseImporter, BaseExporter
from libcore_hng.exceptions.directory_exception import OutputDirectoryNotFoundError

class ExcelImporter(BaseImporter):
    """
    Excelインポートクラス
    """
    
    def __init__(self):
        """
        コンストラクタ
        
        Parameters
        ----------
        use_header : bool, optional
            True の場合はExcelの1行目を列名にする
            False の場合は列名を自動生成する
        """
        
        self.workbooks = None
        """ Excelワークブック """
        
        self.sheets = None
        """ Excelワークシート """
        
        self.filepath = None
        """ Excelファイルパス """

    def _open_book(self, filepath: str):
        """
        Excelブックを開く
        
        Parameters
        ----------
        filepath : str
            ファイルパス
        """
        
        # ファイルパス保持
        self.filepath = filepath
        # ブックの読み込み
        self.workbooks = pd.ExcelFile(filepath)
        # シートの読み込み
        self.sheets = self.workbooks.sheet_names
        
    def load(self, filepath: str, sheet_name: str = None, header_row_index: int | list[int] | None = 0) -> pd.DataFrame:
        """
        ExcelシートをDataFrameとして読み込む
        
        Parameters
        ----------
        filepath : str
            ファイルパス
        sheet_name : str, optional
            シート名。指定しない場合は最初のシートを読み込む。
        header : int, list of int, or None, optional
            列名にする行番号（0始まり）
            - 0 (デフォルト): 1行目を列名にする
            - None: 列名なしで読み込む（自動で 0,1,2,... が付与される）
            - n: n+1 行目を列名にする
            - [0,1]: 複数行を階層的な列名にする (MultiIndex)

        Returns
        -------
        pd.DataFrame
            読み込んだExcelシートのDataFrameオブジェクト
        """

        # ExcelファイルのFullPathを取得
        full_path = os.path.join(bcfg.cfg.project_root_path, filepath)
        
        # ブックを開く
        self._open_book(full_path)
        
        # シート名の指定が無い場合は最初のシートを対象とする
        if sheet_name is None:
            sheet_name = self.sheets[0]
        
        # 指定がない場合は最初のシートを読み込む
        return pd.read_excel(full_path, sheet_name=sheet_name, header=header_row_index)
    
class JsonExporter(BaseExporter):
    """
    JSONエクスポートクラス
    """
    
    def save(self, output_dir: str, filename: str, target_df: pd.DataFrame):
        """
        DataFrameをjsonファイルとして保存する
        
        Parameters
        ----------
        output_dir : str
            出力先ディレクトリパス
        filename : str
            保存するJsonファイル名
        target_df : pd.DataFrame
            保存するDataFrameオブジェクト
        """
        
        # 出力先ディレクトリ存在確認
        if not os.path.isdir(output_dir):
            raise OutputDirectoryNotFoundError(output_dir)
        
        # 拡張子を補完する
        if not filename.lower().endswith('.json'):
            filename += '.json'
        
        # 出力ファイルのFullPathを取得
        if os.path.isabs(output_dir):
            full_path = os.path.join(output_dir, filename)
        else:
            full_path = os.path.join(bcfg.cfg.project_root_path, output_dir, filename)

        # jsonファイル出力
        target_df.to_json(full_path, orient='records', force_ascii=False, indent=4, date_format='iso')
