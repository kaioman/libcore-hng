import libcore_hng.utils.app_core as uwc
from libcore_hng.utils.io_manager import JsonImporter
from libcore_hng.exceptions.directory_exception import DirectoryNotFoundError

# アプリ初期化
uwc.init_app(__file__, "logger.json")

# ソースファイルimport
importer = JsonImporter()
try:
    df = importer.to_dataframe(filepath="tests/data/race_count.json")
    print(df.head())
except DirectoryNotFoundError as e:
    print(f"Caught on exception: {e}")

dict = importer.to_dict(filepath="tests/data/race_count.json")
print(dict)
