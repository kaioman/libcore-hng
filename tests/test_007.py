import libcore_hng.core.base_config as bcfg
import libcore_hng.utils.app_logger as app_logger
from libcore_hng.utils.io_manager import ExcelImporter, JsonExporter
from libcore_hng.exceptions.directory_exception import DirectoryNotFoundError

# 共通設定クラスインスタンス生成
bcfg.cfg = bcfg.BaseConfig.load_config(
    __file__,
    "logger.json"
)

# ロガー設定
app_logger.setting(bcfg.cfg)

# ソースファイルimport
importer = ExcelImporter()
df = importer.to_dataframe(filepath="tests/data/race_count.xlsx")
print(df.head())

# ソースファイルexport
exporter = JsonExporter()
try:
    exporter.save(filepath="tests/data/race_count.json", target_df=df)
except DirectoryNotFoundError as e:
    print(f"Caught on exception: {e}")
