# Gemini CLI - Project Guidelines (libcore-hng)

このプロジェクト(`libcore-hng`)における開発ガイドライン、命名規則、および「このプロジェクトらしい」実装方法をまとめます。
AIアシスタントは本プロジェクト内のコードを編集・生成する際、このガイドラインに厳密に従ってください。

## 1. プロジェクト概要

`libcore-hng` は、多様なAI API（LLM、画像生成等）やライブラリへのアクセスを統合し、スケーラブルなPythonアプリケーションを構築するための軽量なコア・ユーティリティライブラリです。

### 主要機能

* **アプリケーション初期化と設定管理**: `AppInitializer` と `BaseConfig` (Pydanticベース) による、JSONファイルベースの統一的な初期化とグローバル状態管理。
* **汎用ユーティリティ**: 画像処理 (`imageops`)、テキスト操作 (`textops`)、数値計算 (`mathops`)、ファイルI/O管理 (`io_manager`) 等。
* **統合ロギング**: `libcore_hng.utils.app_logger` による、標準化されたログ出力。
* **例外処理基盤**: 各種APIやファイル操作に対応するカスタム例外クラス群。

## 2. 技術スタック

* **言語**: Python 3.8以上
* **ビルド/依存関係管理**: `setuptools` (`pyproject.toml`)
* **主要パッケージ**:
  * `pydantic`: 設定モデルおよびデータバリデーション
  * `pandas` / `openpyxl`: データ処理（Excel等のインポート/エクスポート）
  * `psutil`: システムリソース（ディスク使用量等）の監視
* **外部API連携の基盤**:
  * 多様なAI APIや外部サービスとの連携を想定した、`BaseApiModel` や `AppInitializer` などの抽象化レイヤーを提供。

## 3. ディレクトリ構造

```text
src/libcore_hng/
├── core/          # 基底クラス (Config, IO, API Model等)
├── exceptions/    # 独自例外クラス定義
└── utils/         # ロガー、各種オペレーション, ヘルパー
configs/           # 設定ファイル (JSON)
tests/             # テストコードおよびテスト用データ
```

## 4. 開発ガイドライン

### 4.1. 命名規則 (Naming Conventions)

* **クラス名**: PascalCase (`XClient`, `BaseConfig` など)
* **関数・メソッド・変数名**: snake_case (`init_app`, `media_bytes` など)
* **ファイル・ディレクトリ名**: snake_case (`app_logger.py` など)
* **プライベート属性/メソッド**: プレフィックスに `_` を付与 (`_load_json` など)

### 4.2. 設定と機密情報の管理

**【重要】 `.env` ファイルは絶対に使用・読み込みしないでください。**

* 設定は `configs/` 以下のJSONファイルで管理します。
* アクセスは `app_core` または初期化された `app` オブジェクトの階層構造を経由して行います。
  * 例: `app.core.config.x_api.consumer_key`

### 4.3. ロギング

* `print()` や標準 `logging` の直接呼び出しは避け, 必ず `libcore_hng.utils.app_logger` を使用してください。

### 4.4. 型アノテーション

* すべての関数・メソッドの引数と戻り値に, 型アノテーションを記述してください。
* 戻り値には独自のデータクラスやモデルを積極的に利用してください。

### 4.5. ドキュメンテーション (NumPyスタイル)

PythonのDocStringを記述する際は、必ず **NumPyスタイル** を遵守してください。

#### 正解例

```python
def load_json(self, abs_path: str) -> str:
    """
    設定をJSONから読み込む

    Parameters
    ----------
    abs_path : str
        JSONファイル相対パス

    Returns
    --------
    str
        JSON文字列
    """
```

### 4.6. 例外処理

* サードパーティライブラリの例外は直接伝搬させず、モジュールごとの独自例外クラス（例: `api_exception.py` 内のクラス）でラップして再送出してください。
