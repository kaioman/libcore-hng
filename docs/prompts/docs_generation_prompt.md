GitHub Copilot として、このリポジトリを対象に作業してください。

プロジェクト全体を分析し、以下の設計ドキュメント群を生成してください。
このタスクはドキュメント生成専用タスクです。

生成対象:
- index.md
- architecture.md
- architecture_rules.md
- business_rules.md
- coding_rules.md
- directory_rules.md
- naming_rules.md
- testing_rules.md
- overview.md

要件:
- 出力は日本語で行ってください
- 文体はですます調にしてください
- Markdown 形式で出力してください
- 既存の実装構成と docs の内容を照合してください
- 不整合があれば、設計変更の必要性を明記してください
- 既存ドキュメントに追記できる最小差分でまとめてください
- 本リポジトリ固有のモジュール名に縛られず、汎用的な責務として整理してください
- 生成した Markdown 文書(architecture.mdなど)は、次のディレクトリに保存してください: E:\Dev\030 libcore-hng\libcore-hng\docs\reference
- ただし、`index.md` は docs 配下の入り口ページとして扱い、保存先は E:\Dev\030 libcore-hng\libcore-hng\docs の直下にしてください
- 生成対象のファイルはまだ存在しない場合があるため、既存の実装・設計文書をもとに新規作成してください。
- `index.md` は docs の入口ページとして生成し、生成対象の設計書一覧と参照順を案内する目次ページにしてください。
- overview.md を必ず生成してください。
- overview.md は、このリポジトリ全体の設計ドキュメントにおける概要ページとして作成し、
  プロジェクト全体の主要な責務、構成の概要、設計書の役割をまとめてください。
- overview.md には、`[src]` 参考入力に含まれる主要な Python ファイルやモジュールの代表例を
  Markdown の表形式でまとめてください。
  表には少なくとも「ファイル / モジュール」「主な責務」「代表的な機能または備考」の列を含めてください。
  すべてのファイルを列挙せず、代表的な実装単位や主要機能を中心に整理してください。
- overview.md の内容は、特定のディレクトリ構成（例: utils フォルダ）に依存しない汎用的な説明にしてください。
- `src` のファイル一覧は分析用の参考入力です。ソースコードの修正は行わず、Markdown ファイル生成のみを行ってください。
- 生成した Markdown 文書は指定した出力先ディレクトリに保存し、`src/` や既存ソースコードには変更を加えないでください。
- 出力は Markdown のみとし、ソースファイルの追加・編集・削除を含めないでください。

禁止事項:
- src配下の編集
- 既存Markdownの編集
- 設定ファイルの編集
- テストコードの編集
- PR作成
- コミット作成
- コード提案の適用

許可事項:
- ファイル参照
- ドキュメント生成
- Markdown出力

参考入力:
[docs]
docs-1. E:/Dev/030 libcore-hng/libcore-hng/docs/index.md
docs-2. E:/Dev/030 libcore-hng/libcore-hng/docs/prompts/docs_generation_prompt.md
docs-3. E:/Dev/030 libcore-hng/libcore-hng/docs/reference/architecture.md
docs-4. E:/Dev/030 libcore-hng/libcore-hng/docs/reference/architecture_rules.md
docs-5. E:/Dev/030 libcore-hng/libcore-hng/docs/reference/business_rules.md
docs-6. E:/Dev/030 libcore-hng/libcore-hng/docs/reference/coding_rules.md
docs-7. E:/Dev/030 libcore-hng/libcore-hng/docs/reference/directory_rules.md
docs-8. E:/Dev/030 libcore-hng/libcore-hng/docs/reference/naming_rules.md
docs-9. E:/Dev/030 libcore-hng/libcore-hng/docs/reference/testing_rules.md
docs-10. E:/Dev/030 libcore-hng/libcore-hng/docs/reference/utils_overview.md

[src]
src-1. E:/Dev/030 libcore-hng/libcore-hng/src/libcore_hng/__init__.py
src-2. E:/Dev/030 libcore-hng/libcore-hng/src/libcore_hng/cli/__init__.py
src-3. E:/Dev/030 libcore-hng/libcore-hng/src/libcore_hng/cli/decrypt_to_encrypt.py
src-4. E:/Dev/030 libcore-hng/libcore-hng/src/libcore_hng/cli/docs_prompt.py
src-5. E:/Dev/030 libcore-hng/libcore-hng/src/libcore_hng/configs/gcp.py
src-6. E:/Dev/030 libcore-hng/libcore-hng/src/libcore_hng/configs/logger.py
src-7. E:/Dev/030 libcore-hng/libcore-hng/src/libcore_hng/core/base_api_model.py
src-8. E:/Dev/030 libcore-hng/libcore-hng/src/libcore_hng/core/base_app_exception.py
src-9. E:/Dev/030 libcore-hng/libcore-hng/src/libcore_hng/core/base_config.py
src-10. E:/Dev/030 libcore-hng/libcore-hng/src/libcore_hng/core/base_config_model.py
src-11. E:/Dev/030 libcore-hng/libcore-hng/src/libcore_hng/core/base_io.py
src-12. E:/Dev/030 libcore-hng/libcore-hng/src/libcore_hng/exceptions/__init__.py
src-13. E:/Dev/030 libcore-hng/libcore-hng/src/libcore_hng/exceptions/api_exception.py
src-14. E:/Dev/030 libcore-hng/libcore-hng/src/libcore_hng/exceptions/config_exception.py
src-15. E:/Dev/030 libcore-hng/libcore-hng/src/libcore_hng/exceptions/crypto_exception.py
src-16. E:/Dev/030 libcore-hng/libcore-hng/src/libcore_hng/exceptions/directory_exception.py
src-17. E:/Dev/030 libcore-hng/libcore-hng/src/libcore_hng/exceptions/file_exception.py
src-18. E:/Dev/030 libcore-hng/libcore-hng/src/libcore_hng/exceptions/filesystem_exception.py
src-19. E:/Dev/030 libcore-hng/libcore-hng/src/libcore_hng/runpod/__init__.py
src-20. E:/Dev/030 libcore-hng/libcore-hng/src/libcore_hng/runpod/core/manager.py
src-21. E:/Dev/030 libcore-hng/libcore-hng/src/libcore_hng/runpod/models/__init__.py
src-22. E:/Dev/030 libcore-hng/libcore-hng/src/libcore_hng/runpod/models/config.py
src-23. E:/Dev/030 libcore-hng/libcore-hng/src/libcore_hng/runpod/models/pod.py
src-24. E:/Dev/030 libcore-hng/libcore-hng/src/libcore_hng/runpod/pod_manager.py
src-25. E:/Dev/030 libcore-hng/libcore-hng/src/libcore_hng/testmodule.py
src-26. E:/Dev/030 libcore-hng/libcore-hng/src/libcore_hng/utils/app_core.py
src-27. E:/Dev/030 libcore-hng/libcore-hng/src/libcore_hng/utils/app_logger.py
src-28. E:/Dev/030 libcore-hng/libcore-hng/src/libcore_hng/utils/app_logger_mixin.py
src-29. E:/Dev/030 libcore-hng/libcore-hng/src/libcore_hng/utils/crypto.py
src-30. E:/Dev/030 libcore-hng/libcore-hng/src/libcore_hng/utils/enums.py
src-31. E:/Dev/030 libcore-hng/libcore-hng/src/libcore_hng/utils/file_renamer.py
src-32. E:/Dev/030 libcore-hng/libcore-hng/src/libcore_hng/utils/helpers.py
src-33. E:/Dev/030 libcore-hng/libcore-hng/src/libcore_hng/utils/imageops.py
src-34. E:/Dev/030 libcore-hng/libcore-hng/src/libcore_hng/utils/io_manager.py
src-35. E:/Dev/030 libcore-hng/libcore-hng/src/libcore_hng/utils/mathops.py
src-36. E:/Dev/030 libcore-hng/libcore-hng/src/libcore_hng/utils/secret_manager.py
src-37. E:/Dev/030 libcore-hng/libcore-hng/src/libcore_hng/utils/system.py
src-38. E:/Dev/030 libcore-hng/libcore-hng/src/libcore_hng/utils/textops.py
src-39. E:/Dev/030 libcore-hng/libcore-hng/src/libcore_hng/utils/thread_local_helpers.py