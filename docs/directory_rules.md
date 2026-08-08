# ディレクトリ構成ルール

## 1. 基本方針

このリポジトリでは、ソースコード・テスト・設定を明確に分離した構成を維持します。

- [src/libcore_hng](src/libcore_hng) が実装本体
- [tests](tests) がテスト群
- [configs](configs) が設定ファイルの置き場
- [docs](docs) がガイド・ルール類の置き場

## 2. 根拠となるファイル

- [pyproject.toml](pyproject.toml)
  - パッケージの配置先が `src` であることが明示されている
- [src/libcore_hng](src/libcore_hng)
  - コア・例外・ユーティリティを分割配置している
- [tests](tests)
  - テストコードとデータを分離している

## 3. 推奨事項

- 実装コードは [src/libcore_hng](src/libcore_hng) 配下に置く。
- 新しい機能は責務に応じて `core/`、`utils/`、`exceptions/`、`configs/` に切り分ける。
- テスト用データは [tests/data](tests/data) のように専用ディレクトリにまとめる。
- 設定ファイルは [configs](configs) 配下に置き、環境依存値は外部から注入する。
- ドキュメントやルールは [docs](docs) 配下に集約する。
