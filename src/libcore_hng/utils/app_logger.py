import os
import logging
import functools
import libcore_hng.utils.helpers as helper
from libcore_hng.core.base_config import BaseConfig
from libcore_hng.configs.logger import LoggerConfig
from libcore_hng.utils.enums import LogFileNameSuffix as log_sfx
from libcore_hng.utils.thread_local_helpers import ThreadLocalDepth

# ネストの深さを管理する変数
thread_local = ThreadLocalDepth()
thread_local.depth = 0

# 共通設定
logger_config: LoggerConfig | None = None

def loggerDecorator(outputString, args_print = []):

    """
    関数の開始～終了でコンソールに文字列を出力するデコレーター
    """

    def _loggerDecorator(func):

        """
        関数の開始～終了でコンソールに文字列を出力するデコレーター
        """

        @functools.wraps(func)
        def wrapper(*args, **kwargs):

            """
            デコレーターのラッパー
            """
            
            # 関数名の出力
            funcName = '(🟢 {0}) ... Execute'.format(outputString)
            print(funcName)
            logging.info(funcName)

            # 引数の出力
            if len(args_print) > 0 and len(kwargs) > 0:
                for argsStr in args_print:
                    if kwargs.get(argsStr) == None : continue
                    argsValue = 'args:{0}={1}'.format(str(argsStr), str(kwargs.get(argsStr)))
                    print(argsValue)
                    logging.info(argsValue)

            try:
                # 関数本体の実行
                ret = func(*args, **kwargs)
                
                # 実行終了の出力
                funcEnded = '(🔵 {0}) ... OK'.format(outputString)
                print(funcEnded)
                logging.info(funcEnded)

            except Exception as e:
                
                # 例外時エラーメッセージ
                errorInfo = "( 🔴 ERROR ) " + func.__name__ + "\n"\
                            "=== エラー内容 ===\n"\
                            "type: {0}\n"\
                            "args: {1}\n"\
                            "e自身: {2}".format(str(type(e)), str(e.args), str(e))
                            
                # エラーメッセージの出力
                logging.error(errorInfo)

                # 例外スロー
                raise 
            
            return ret

        return wrapper

    return _loggerDecorator

def setting(base_cfg: BaseConfig):

    """
    ロガー設定

    Parameters
    ----------
    log_cfg : BaseConfig
        共通設定クラス
    """

    # ログ出力先がない場合、作成する
    if os.path.exists(base_cfg.project_root_path / base_cfg.logging.logfolder_name) == False:
        os.mkdir(base_cfg.logging.logfolder_name)

    # ログファイル名サフィックス設定
    logFileName = getLogFileName(base_cfg.logging)
    
    # ロガー設定
    logging.basicConfig(
        filename=os.path.join(base_cfg.logging.logfolder_name, logFileName),
        level=base_cfg.logging.loglevel, 
        format=base_cfg.logging.logformat)

    # 共通設定をグローバル変数に保存
    global logger_config
    logger_config = base_cfg.logging
    
def getLogFileName(log_cfg: LoggerConfig):
    
    """
    ログファイル名取得

    Parameters
    ----------
    log_cfg : LoggerConfig
        ロガー設定クラス
    """
    
    # 既定ログファイル名取得
    logFileName = log_cfg.logfile_name
    # ログファイル名サフィックス判定
    if log_cfg.logfile_name_suffix != log_sfx.suffixNone.value:
        
        # 拡張子を除いたファイル名取得
        logFileName_format = os.path.splitext(logFileName)[0] + '_{0}' + os.path.splitext(logFileName)[1]
        
        # ログファイル名にサフィックスを付与する
        fmt = getattr(helper.DatetimeFormat, log_sfx.value_of(log_cfg.logfile_name_suffix))
        logFileName = logFileName_format.format(helper.get_now(fmt))

    # 戻り値を返す
    return logFileName

def set_depth(depth: int):
    
    # ネストの深さを設定
    thread_local.depth = depth

def get_indent() -> str:
    """
    ネストの深さに応じたインデント文字列を生成する
    
    Parameters
    ----------
    None
    """
    depth = thread_local.depth
    return logger_config.log_depth * depth + " "

def console_log(message: str):
    """
    コンソールにメッセージを出力する
    
    Parameters
    ----------
    message : str
        出力するメッセージ
    """
    print(message)

def get_log_prefix(prefix_emoji: str, prefix_string: str):
    """
    ログプレフィックスを取得する
    
    Parameters
    ----------
    prefix_emoji : str
        ログプレフィックスとして出力する絵文字
    prefix_string : str
        ログプレフィックスとして出力する文字列
    """
    return logger_config.log_prefix_format.format(prefix_emoji, prefix_string.ljust(6) if prefix_string else "(unknown)")

def get_method_start_prefix():
    """
    メソッドStartログのプレフィックスを取得する
    """
    return get_log_prefix(logger_config.log_method_start_emoji, logger_config.log_method_start_string)

def get_method_end_prefix():
    """
    メソッドEndログのプレフィックスを取得する
    """
    return get_log_prefix(logger_config.log_method_end_emoji, logger_config.log_method_end_string)

def get_error_prefix():
    """
    Errorログのプレフィックスを取得する
    """
    return get_log_prefix(logger_config.log_error_emoji, logger_config.log_error_string)

def get_error_caption():
    """
    ErrorログのCaptionを取得する
    """
    return get_log_prefix(logger_config.log_error_caption_emoji, logger_config.log_error_caption_string)

def get_warning_prefix():
    """
    Warningログのプレフィックスを取得する
    """
    return get_log_prefix(logger_config.log_warning_emoji, logger_config.log_warning_string)

def get_proc_prefix():
    """
    Procログのプレフィックスを取得する
    """
    return get_log_prefix(logger_config.log_proc_emoji, logger_config.log_proc_string)

def start_method(method_name: str, args_repr: str = ""):
    """
    メソッドの開始ログを出力する
    
    Parameters
    ----------
    method_name : str
        メソッド名
    args_repr : str, optional
        引数の文字列表現
    """
    # メッセージ生成
    logMessage = get_indent() + f"{get_method_start_prefix()} { method_name }" + ("" if args_repr == "" else " | args=(" + args_repr + ")")
    # コンソール出力
    console_log(logMessage)
    # ログ出力
    return logging.info(logMessage)

def end_method(method_name: str, returnVal = None):
    """
    メソッドの終了ログを出力する
    
    Parameters
    ----------
    method_name : str
        メソッド名
    args_repr : str, optional
        メソッドの戻り値
    """
    # メッセージ生成
    logMessage = get_indent() + f"{get_method_end_prefix()} { method_name }" + ("" if returnVal == None else f" | return=({ returnVal })")
    # コンソール出力
    console_log(logMessage)
    # ログ出力
    return logging.info(logMessage)

def error(method_name, e: Exception):
    """
    例外発生時のエラーログを出力する
    
    Parameters
    ----------
    method_name : str
        メソッド名
    e : Exception
        発生した例外
    """
    # エラーメッセージ生成
    errorInfoArray = [
        f"{ get_error_prefix() } { method_name }",
        f"{ get_error_caption() }",
        "type: {0}",
        "args: {1}",
        "exception: {2}"
    ]
    # ネストの深さに応じてインデントを追加
    errorInfo = ''
    for info in errorInfoArray:
        # エラーメッセージ文字列の前後にインデントと改行を追加
        errorInfo += get_indent() + info + "\n"
    errorInfo = errorInfo.format(str(type(e)), str(e.args), str(e))
    # コンソール出力
    console_log(errorInfo)
    # ログ出力
    return logging.error(errorInfo)

def error(message: str, console_logging: bool = True):
    """
    エラーログを出力する

    Parameters
    ----------
    message : str
        出力するメッセージ
    consoleLogging : bool
        コンソール出力有無
    """
    # メッセージ生成
    logMessage = get_indent() + f"{ get_error_prefix() } { message }"
    # コンソール出力
    if console_logging:
        console_log(logMessage)
    # ログ出力
    return logging.error(logMessage)
    
def warning(message: str, console_logging: bool = True):
    """
    警告ログを出力する

    Parameters
    ----------
    message : str
        出力するメッセージ
    consoleLogging : bool
        コンソール出力有無
    """
    # メッセージ生成
    logMessage = get_indent() + f"{ get_warning_prefix() } { message }"
    # コンソール出力
    if console_logging:
        console_log(logMessage)
    # ログ出力
    return logging.warning(logMessage)

def info(message: str, console_logging: bool = True):
    """
    処理ログを出力する

    Parameters
    ----------
    message : str
        出力するメッセージ
    consoleLogging : bool
        コンソール出力有無
    """
    # メッセージ生成
    logMessage = get_indent() + f"{ get_proc_prefix() } { message }"
    # コンソール出力
    if console_logging:
        console_log(logMessage)
    # ログ出力
    return logging.info(logMessage)