import inspect
import libcore_hng.utils.app_logger as app_logger
from libcore_hng.utils.thread_local_helpers import ThreadLocalDepth

# ネストの深さをスレッドローカルで管理
thread_local = ThreadLocalDepth()
thread_local.depth = 0

class LoggingMixin:
    
    """
    ログ出力Mixinクラス
    BaseModelなどと多重継承して利用することを想定
    """
    
    def __init_subclass__(cls, **kwargs):
        
        # サブクラスのメソッドをラップする
        super().__init_subclass__(**kwargs)
        
        for attr_name, attr_value in cls.__dict__.items():
            if attr_name.startswith("__") and attr_name.endswith("__"):
                continue
            if callable(attr_value):
                setattr(cls, attr_name, cls.wrap_method(attr_name, attr_value))

    @staticmethod
    def wrap_method(method_name, method):
        
        """
        メソッドをラップするデコレーター
        
        Parameters
        ----------
        method_name : Any
            メソッド名
        method : Any
            ラップするメソッド
        """
        
        def wrapper(*args, **kwargs):
            
            """
            メソッドの開始と終了をログに出力するラッパー
            """
            
            if not hasattr(thread_local, 'depth'):
                thread_local.depth = 0
            
            # ネストレベルを上げる
            thread_local.depth += 1
            app_logger.set_depth(thread_local.depth)
            
            # 引数の出力
            sig = inspect.signature(method)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            args_repr = ''
            if bound_args:
                args_repr = ", ".join(f"{key}:{value}" for key, value in bound_args.arguments.items() if key != "self")

            # 戻り値変数初期化
            ret = None

            try:
            
                # 開始ログの出力
                app_logger.start_method(method_name, args_repr)
                
                # 関数本体の実行
                ret = method(*args, **kwargs)
                                
            except Exception as e:
                
                # エラーメッセージの出力
                app_logger.error(method_name, e)

                # 例外スロー
                raise

            finally:
                
                # 終了ログの出力
                app_logger.end_method(method_name, ret)
                
                # ネストレベルを戻す
                thread_local.depth -= 1
                app_logger.set_depth(thread_local.depth)

            return ret
        return wrapper