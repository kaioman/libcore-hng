import libcore_hng.core.base_config as bcfg
import libcore_hng.utils.app_logger as app_logger
from typing import TypeVar, Generic

T = TypeVar("T", bound=bcfg.BaseConfig)

class AppInitializer(Generic[T]):
    """
    アプリケーションコアクラス

    - 共通設定クラスインスタンス生成
    - ロガー設定
    """

    def __init__(self, config_cls: type[T], base_file: str = __file__, *config_file: str):
        """
        コンストラクタ

        Parameters
        ----------
        config_cls : type[T]
            設定クラス。BaseConfig を継承したクラスを指定し、
            アプリケーション固有の設定ロードや初期化処理に利用する        
        base_file : str, optional
            基準となるファイルパス (デフォルト: __file__)
        *config_file : str, optional
            ロガー設定ファイル名やその他設定ファイル
            BaseConfig.load_config にそのまま渡されるため、複数指定可能

        Returns
        -------
        BaseConfig
            ロードされた設定インスタンス
        """

        # デフォルト値補完
        if not config_file:
            config_file = ("logger.json")
        
        # 共通設定クラスインスタンス生成
        self.config: T = config_cls.load_config(base_file, *config_file)

        # ロガー設定
        app_logger.setting(self.config)
        
core: AppInitializer[T] | None = None
""" アプリケーション初期化済みインスタンスを保持するグローバル変数 """

def init_app(config_cls: type[T], base_file: str = __file__, *config_file: str) -> AppInitializer[T]:
    """
    アプリケーションの初期化処理を一度だけ実行する関数

    - BaseConfig.load_config を呼び出して共通設定をロード
    - ロガー設定を適用
    - グローバル変数 app_core に AppInitializer インスタンスを格納

    Parameters
    ----------
    config_cls : type[T]
        設定クラス。BaseConfig を継承したクラスを指定し、
        アプリケーション固有の設定ロードや初期化処理に利用する
    base_file : str, optional
        基準となるファイルパス (デフォルト: __file__)
    *config_file : str, optional
        設定ファイル群。指定がない場合は "logger.json" が使用される。
        複数指定可能で、BaseConfig.load_config にそのまま渡される。

    Returns
    -------
    AppInitializer
        初期化済みの AppInitializer インスタンス。
        グローバル変数 app_core にも格納されるため、他モジュールから参照可能。
    """

    global core
    core = AppInitializer(config_cls, base_file, *config_file)
    return core