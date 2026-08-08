# コーディングルール

## 1. 基本方針

このプロジェクトでは、Python の標準的な構造に加えて、以下の実装スタイルを採用します。

- 型注釈を積極的に利用する
- クラスベースの構造を基本とする
- 例外は独自クラスでラップして扱う
- ログ出力は専用ユーティリティを通して行う
- 既存の基底クラスを継承して拡張する

## 2. 根拠となるファイル

- [src/libcore_hng/core/base_config.py](src/libcore_hng/core/base_config.py)
  - 型注釈付きのクラスメソッド実装
- [src/libcore_hng/core/base_app_exception.py](src/libcore_hng/core/base_app_exception.py)
  - 独自例外基底クラスの実装
- [src/libcore_hng/utils/file_renamer.py](src/libcore_hng/utils/file_renamer.py)
  - 明示的な戻り値型と例外ハンドリング
- [src/libcore_hng/utils/app_logger.py](src/libcore_hng/utils/app_logger.py)
  - ログ処理の共通化

## 3. 推奨事項

- 関数・メソッドには必ず型注釈を付ける。
- 例外は `raise ... from e` の形で元の例外を保持する。
- 直接 `print()` ではなく、必要に応じてロギングユーティリティを使う。
- 複雑な処理は小さな責務に分けて実装する。
- 既存の基底クラスや抽象クラスを尊重し、拡張箇所は最小限にする。
