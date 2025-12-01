import libcore_hng.core.base_config as bcfg
import libcore_hng.utils.app_logger as app_logger

# 共通設定クラスインスタンス生成
bcfg.cfg = bcfg.BaseConfig.load_config(
    __file__,
    "logger.json"
)
print(bcfg.cfg.logging.logfile_name)

# ロガー設定
app_logger.setting(bcfg.cfg)
