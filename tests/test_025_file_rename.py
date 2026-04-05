import libcore_hng.utils.app_core as app
from libcore_hng.utils.file_renamer import FileRenamer
from libcore_hng.core.base_config import BaseConfig

# アプリ初期化
app.init_app(BaseConfig, __file__, "app_config.json")

target_dir = "D:\\OneDrive\\02 Picture\\アバター\\LoRA\\Aoi\\Tags"
backup_dir = "D:\\OneDrive\\02 Picture\\アバター\\LoRA\\Aoi\\Tags\\backup"

# FileRenamerのインスタンスを作成
renamer = FileRenamer(target_dir)

print("\n--- Actual Rename (pngファイルのみ、prefix 'aoi_', 連番開始1, バックアップあり) ---") # 変更
results = renamer.rename_files(prefix="aoi_", extension="png", start_index=1, dry_run=True, backup_directory=backup_dir) # 変更
for res in results:
    print(res)

