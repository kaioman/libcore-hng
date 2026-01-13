import logging
from libcore_hng.core.base_config_model import BaseConfigModel
from libcore_hng.utils.enums import LogFileNameSuffix as log_sfx

class LoggerConfig(BaseConfigModel):
    """
    ロガー共通設定クラス
    """
    
    logfile_name: str = "default.log"
    """ ログファイル名 """
    
    logfile_name_suffix: int = log_sfx.suffixNone
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

    log_method_end_emoji: str = '🟢'
    """ ログメソッドEnd絵文字 """
    log_method_end_string: str = 'END   '
    """ ログメソッドEnd文字列 """

    log_error_emoji: str = '❌'
    """ ログError絵文字 """
    log_error_string: str = 'ERROR '
    """ ログError文字列 """

    log_error_caption_emoji: str = '🔴'
    """ ログErrorCaption絵文字 """
    log_error_caption_string: str = 'Error Occurred'
    """ ログErrorCaption文字列 """

    log_warning_emoji: str = '⚠️'
    """ ログWarning絵文字 """
    log_warning_string: str = 'WARN  '
    """ ログWarning文字列 """

    log_proc_emoji: str = '🔵'
    """ ログProc絵文字 """
    log_proc_string: str = 'PROC  '
    """ ログProc文字列 """
    
    log_depth: str = "+"
    """ インデント文字列 """
    
    log_interval: int = 1
    """ ログインターバル """
    
    log_backupCount: int = 7
    """ ログバックアップ数 """
    
    log_rotation_when: str = "midnight"
    """ 
    ローテーションタイミング
    
    - S:秒ごと
    - M:分ごと
    - H:時ごと
    - D:日ごと(0時)
    - midnight:日ごと(0時) Dと同じ意味
    - W0～W6:曜日ごと(0=月曜～6=日曜)
    """
    
    log_file_encording: str = "utf-8"
    """ ログファイルエンコード """
    
    log_rotation_utc_time: bool = False
    """ ローテーションをutc時間で実施する """