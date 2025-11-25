import libcore_hng.core.base_config as bcfg

bcfg.cfg = bcfg.BaseConfig.load_config(
    __file__,
    "logger.json"
)

print(bcfg.cfg.logging.logfile_name)
