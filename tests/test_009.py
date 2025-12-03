import libcore_hng.utils.app_core as app
from libcore_hng.utils.io_manager import JsonImporter
from libcore_hng.exceptions.directory_exception import DirectoryNotFoundError
from libcore_hng.core.base_config import BaseConfig

# アプリ初期化
app.init_app(BaseConfig, __file__, "logger.json")

# app_core確認
print(app.core.config.logging.logfolder_name)

# ソースファイルimport  
importer = JsonImporter()
try:
    df = importer.to_dataframe(filepath="tests/data/race_count.json")
    print(df.head())
except DirectoryNotFoundError as e:
    print(f"Caught on exception: {e}")

dict = importer.to_dict(filepath="tests/data/race_count.json")
print(dict)
