import os
import json
import pandas as pd
import libcore_hng.utils.system as sys
import libcore_hng.utils.app_core as uwc
from libcore_hng.core.base_io import BaseImporter, BaseExporter

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
        
    def to_dataframe(self, filepath: str, sheet_name: str = None, header_row_index: int | list[int] | None = 0) -> pd.DataFrame:
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
        full_path = os.path.join(uwc.core.config.project_root_path, filepath)
        
        # ブックを開く
        self._open_book(full_path)
        
        # シート名の指定が無い場合は最初のシートを対象とする
        if sheet_name is None:
            sheet_name = self.sheets[0]
        
        # 指定がない場合は最初のシートを読み込む
        return pd.read_excel(full_path, sheet_name=sheet_name, header=header_row_index)

class JsonImporter(BaseImporter):
    """
    Jsonファイルインポートクラス
    """

    def to_dataframe(self, filepath: str) -> pd.DataFrame:
        """
        JSONファイルを読み込み、DataFrameに変換する
        
        Parameters
        ----------
        filepath : str
            ファイルパス

        Returns
        -------
        pd.DataFrame
            JSONデータをDataFrameに変換したオブジェクト
        """

        # ファイルパスから出力先ディレクトリ、ファイル名を分割
        output_dir, filename = sys.split_path(filepath)
        
        # 入力ディレクトリ存在確認
        self.exists_directory(output_dir)

        # 拡張子を補完する
        filename = sys.ensure_extenstion(filename, 'json')
        
        # jsonファイルのFullPathを取得
        full_path = self.get_fullpath(output_dir, filename)
        
        # jsonファイルをdict型で取得する
        dict_json = self.to_dict(full_path)
        
        # dictをdataframeに変換する(キーをカラム名とする)
        return pd.DataFrame(dict_json)
        
    def to_dict(self, filepath: str) -> dict:
        """
        JSONファイルを読み込み、dictに変換する
        
        Parameters
        ----------
        filepath : str
            ファイルパス

        Returns
        -------
        dict
            JSONデータをdict型に変換したオブジェクト
        """
        
        # jsonファイルを開く
        with self.get_json_file(filepath) as file_json:
        
            # jsonファイルをロードする
            return json.load(file_json)

    def get_json_file(self, filepath: str):
        """
        JSONファイルを開いてファイルオブジェクトを返す
        
        Parameters
        ----------
        filepath : str
            ファイルパス

        Returns
        -------
        TextIOWrapper
            開いたJSONファイルのファイルオブジェクト
        """

        # jsonファイルを開く
        return open(filepath, 'r', encoding='utf-8')
    
class JsonExporter(BaseExporter):
    """
    JSONエクスポートクラス
    """
    
    def save(self, filepath: str, target_df: pd.DataFrame):
        """
        DataFrameをjsonファイルとして保存する
        
        Parameters
        ----------
        filepath : str
            ファイルパス
        target_df : pd.DataFrame
            保存するDataFrameオブジェクト
        """

        # ファイルパスから出力先ディレクトリ、ファイル名を分割
        output_dir, filename = sys.split_path(filepath)
        
        # 出力先ディレクトリ存在確認
        self.exists_directory(output_dir)
        
        # 拡張子を補完する
        filename = sys.ensure_extenstion(filename, 'json')
        
        # 出力ファイルのFullPathを取得
        full_path = self.get_fullpath(output_dir, filename)

        # jsonファイル出力
        target_df.to_json(full_path, orient='records', force_ascii=False, indent=4, date_format='iso')
