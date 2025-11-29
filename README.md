# libcore-hng

A lightweight Python core package designed to unify access to diverse AI APIs and libraries. It provides a consistent, scalable foundation for building modular applications with clarity and flexibility.

## アプリ初期処理サンプル

このプロジェクトでは、`AppInitializer` を用いてアプリケーションの初期化処理を行います。  
初期化は一度だけ実行し、以降はグローバルインスタンス `app_core` を参照してください。

---

### 初期化方法

```python
import libcore_hng.utils.app_core as uwc

# アプリ初期化（最初の一度だけ呼び出す）
uwc.init_app(__file__, "logger.json")

# 以降はグローバルインスタンスを参照
print(uwc.ins.config.project_root_path)
