import libcore_hng.utils.app_core as uwc
from libcore_hng.utils.io_manager import ExcelImporter, JsonExporter
from libcore_hng.exceptions.directory_exception import DirectoryNotFoundError

# アプリ初期化
uwc.init_app(__file__, "logger.json")

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
