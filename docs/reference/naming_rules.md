# 命名規則

## 1. 基本方針

このリポジトリでは、Python らしい命名規則を一貫して適用します。

- クラス名は PascalCase
- 関数・メソッド・変数名は snake_case
- モジュール名・ディレクトリ名は snake_case
- プライベート属性・メソッドには `_` を付与

## 2. 根拠となるファイル

- [src/libcore_hng/core/base_config.py](src/libcore_hng/core/base_config.py)
  - `BaseConfig`, `load_config`, `project_root_path`
- [src/libcore_hng/utils/app_core.py](src/libcore_hng/utils/app_core.py)
  - `AppInitializer`, `init_app`, `config_cls`
- [src/libcore_hng/utils/file_renamer.py](src/libcore_hng/utils/file_renamer.py)
  - `_backup_file`, `rename_files`, `backup_directory`

## 3. 推奨事項

- 既存の命名規則に合わせて新しいシンボルを追加する。
- 省略形や略語は避け、意味が伝わる名前を使う。
- プライベートな内部状態は `_` 付きで明示する。
- 既存の `Base*` / `App*` / `*Config` などの命名パターンを踏襲する。
