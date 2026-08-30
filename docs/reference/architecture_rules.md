# アーキテクチャルール

## 1. 基本方針

このリポジトリでは、設定管理・ロギング・例外処理・ユーティリティ関数を提供する Python コアライブラリとして設計します。主要な責務は次の 4 つに分けて管理します。

- コア基盤: [src/libcore_hng/core](src/libcore_hng/core) 配下の基底クラス群
- 設定・構成: [src/libcore_hng/configs](src/libcore_hng/configs) 配下の設定モデル
- 例外・エラー処理: [src/libcore_hng/exceptions](src/libcore_hng/exceptions) 配下の独自例外
- ユーティリティ: [src/libcore_hng/utils](src/libcore_hng/utils) 配下の各モジュール

## 2. バージョン管理方針

- バージョン更新は release ブランチでのみ実施する
- tbump による変更は main ブランチへマージしない
- main ブランチのバージョン番号は最新リリースと一致しない場合がある
- PyPI の公開バージョンを正とする

## 3. 根拠となるファイル

- [src/libcore_hng/core/base_config.py](src/libcore_hng/core/base_config.py)
  - 設定ロードとプロジェクトルート解決を担当
- [src/libcore_hng/utils/app_core.py](src/libcore_hng/utils/app_core.py)
  - アプリ初期化とグローバルインスタンス管理を担当
- [src/libcore_hng/utils/app_logger.py](src/libcore_hng/utils/app_logger.py)
  - ロギング設定の統一入口
- [src/libcore_hng/core/base_app_exception.py](src/libcore_hng/core/base_app_exception.py)
  - 例外ラッパーの基底実装

## 4. 推奨事項

- 新しい機能は「コア」「ユーティリティ」「例外」「設定」の責務に分けて追加する。
- 依存関係は上位モジュールから下位モジュールへ一方向に流れるように保つ。
- アプリケーション全体の初期化は [src/libcore_hng/utils/app_core.py](src/libcore_hng/utils/app_core.py) を通して行う。
- ログや例外の扱いは共通基盤に寄せて、個別モジュールが独自ルールを持たないようにする。
