import json
import os
import logging
from pathlib import Path
from pydantic import BaseModel
from libcore_hng.utils.filepath_manager import find_project_root
from libcore_hng.utils.enums import logFileNameSuffix

class LoggerConfig(BaseModel):
    """
    ロガー共通設定クラス
    """
    
    logfile_name: str = "default.log"
    """ ログファイル名 """
    
    logfile_name_suffix: int = logFileNameSuffix.suffixNone
    """ ログファイル名サフィックス """
    
    logfolder_name: str = "./log"
    """ ログ出力先フォルダ名 """
    
    logformat: str = "%(levelname)-7s : %(asctime)s : %(message)s"
    """ ログフォーマット定義 """

    loglevel: int = logging.DEBUG
    """ ログレベル """
    
    log_prefix_format: str = "[ {} {} ]"
    """ ログプレフィックスフォーマット """
    
    log_method_start_emoji: str = '🟢'
    """ ログメソッドStart絵文字 """
    log_method_start_string: str = 'START '
    """ ログメソッドStart文字列 """

    Log_method_end_emoji: str = '🟢'
    """ ログメソッドEnd絵文字 """
    Log_method_end_string: str = 'END   '
    """ ログメソッドEnd文字列 """

    log_error_emoji: str = '❌'
    """ ログError絵文字 """
    Log_error_string: str = 'ERROR '
    """ ログError文字列 """

    Log_error_caption_emoji: str = '🔴'
    """ ログErrorCaption絵文字 """
    Log_error_caption_string: str = 'Error Occurred'
    """ ログErrorCaption文字列 """

    Log_warning_emoji: str = '⚠️'
    """ ログWarning絵文字 """
    Log_warning_string: str = 'WARN  '
    """ ログWarning文字列 """

    Log_proc_emoji: str = '🔵'
    """ ログProc絵文字 """
    Log_proc_string: str = 'PROC  '
    """ ログProc文字列 """
    
    log_depth: str = "+"
    """ インデント文字列 """

class BaseConfig(BaseModel):
    
    logger: LoggerConfig = LoggerConfig()
    """ ロガー共通設定 """

    @classmethod
    def load_config(cls, caller_file: str, *file_names: str, config_dir: Path | None = None) -> "BaseConfig":
        """
        設定ファイルを読み込む
        
        Parameters
        ----------

        caller_file : str
            呼び出し元ファイルの__file__
        file_names : str
            設定ファイル名のか可変長引数
        config_dir : Path
            設定ファイルのディレクトリ
            指定時はPathオブジェクトで指定する 例：Path("path/to/configs")
        """
        
        if config_dir is None:
            # 環境変数CONFIG_DIRの設定有無を確認
            if "CONFIG_DIR" in os.environ:
                # 環境変数より設定ファイル格納パスを取得
                config_dir = Path(os.environ["CONFIG_DIR"]).resolve()
            else:
                # プロジェクトルートパスを取得
                project_root = find_project_root(Path(caller_file))

                # 設定ファイル格納パスを取得
                config_dir = project_root / "configs"

        # 設定ファイルを読み込んでマージする
        merged = {}
        for file_name in file_names:
            config_path = config_dir / file_name
            if config_path.exists():
                with open(config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    merged.update(data)
        
        # 自クラスインスタンスを共通設定クラスインスタンスとして返す
        return cls(**merged)