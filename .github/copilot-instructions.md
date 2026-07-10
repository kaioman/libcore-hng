# Copilot Instructions for libcore-hng

このファイルは、GitHub Copilot がこのリポジトリでコード生成・修正・リファクタリング・テスト作成を行う際に従うべき基本方針です。

## 必須参照ドキュメント

コード生成・修正前に、以下のドキュメントを必ず確認してください。

- [docs/architecture.md](../docs/architecture.md)
- [docs/business_rules.md](../docs/business_rules.md)
- [docs/architecture_rules.md](../docs/architecture_rules.md)
- [docs/coding_rules.md](../docs/coding_rules.md)
- [docs/directory_rules.md](../docs/directory_rules.md)
- [docs/naming_rules.md](../docs/naming_rules.md)
- [docs/testing_rules.md](../docs/testing_rules.md)

## 必須方針

1. コード生成前に関連ドキュメントを確認すること
2. ドキュメントに反する実装を提案しないこと
3. [docs/business_rules.md](../docs/business_rules.md) に記載された業務ルールを優先すること
4. [docs/architecture_rules.md](../docs/architecture_rules.md) に記載されたアーキテクチャルールを遵守すること
5. [docs/coding_rules.md](../docs/coding_rules.md) に記載されたコーディングルールを遵守すること
6. [docs/naming_rules.md](../docs/naming_rules.md) に記載された命名規則を遵守すること
7. [docs/testing_rules.md](../docs/testing_rules.md) に従ってテストを作成すること
8. [docs/directory_rules.md](../docs/directory_rules.md) に従ってファイル配置を行うこと
9. ドキュメントと実装の不整合を発見した場合は指摘すること
10. 設計変更が必要な場合はドキュメント更新も提案すること

## 優先順位

1. [docs/business_rules.md](../docs/business_rules.md)
2. [docs/architecture_rules.md](../docs/architecture_rules.md)
3. [docs/coding_rules.md](../docs/coding_rules.md)
4. [docs/naming_rules.md](../docs/naming_rules.md)
5. [docs/testing_rules.md](../docs/testing_rules.md)
6. [docs/directory_rules.md](../docs/directory_rules.md)

## 追加の基本方針

- 既存の実装パターンに合わせること
- 変更は最小限に留め、既存動作を壊さないこと
- 機密情報は平文で扱わず、既存の設定・暗号化・ロギング基盤を利用すること
- テストは必要に応じて追加・更新すること
