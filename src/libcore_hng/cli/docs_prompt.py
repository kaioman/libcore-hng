from __future__ import annotations

import argparse
from pathlib import Path

def resolve_project_root(project_root: str | Path | None) -> Path:
    """
    リポジトリルートを安定して解決する

    Parameters
    ----------
    project_root : str | Path | None
        明示指定されたプロジェクトルート
        未指定時はカレントディレクトリをプロジェクトルートとする
    """
    if project_root is not None:
        return Path(project_root).resolve()
    return Path.cwd().resolve()

def collect_project_inputs(project_root: str | Path | None) -> dict[str, list[Path]]:
    """
    プロジェクトの docs と src のファイルを収集する

    Parameters
    ----------
    project_root : str | Path | None
        プロジェクトルートパス

    Returns
    -------
    dict[str, list[Path]]
        参考ファイルのパスリスト
        docsフォルダ、srcフォルダ別に保持する
    """

    # ルートパスを取得する
    base_root = Path(project_root).resolve() if project_root is not None else Path.cwd().resolve()

    # docsフォルダルート
    docs_root = base_root / "docs"
    # srcフォルダルート
    src_root = base_root / "src"

    # docsルートが存在しない場合
    if not docs_root.exists():
        return {"docs": [], "src": []}
    # docsルートは存在、srcルートが存在しない場合
    if not src_root.exists():
        return {"docs": sorted(docs_root.rglob("*.md"))}

    # docsフォルダにあるmdファイルパスを取得
    docs_files = sorted(docs_root.rglob("*.md"))
    # srcフォルダにあるpyファイルパスを取得
    src_files = sorted(
        [path for path in src_root.rglob("*.py") if path.is_file()]
    )

    # 取得結果を返す
    return {
        "docs": docs_files,
        "src": src_files,
    }

def build_docs_generation_prompt(inputs: dict[str, list[Path]], output_dir: Path) -> str:
    """
    ドキュメント生成用のプロンプトを構築する

    Parameters
    ----------
    inputs : dict[str, list[Path]]
        参考ファイルのパスリスト
    output_dir : str
        指示プロンプトファイルの出力先パス
    
    Returns
    -------
    str
        ドキュメント生成指示プロンプト
    """
    # docsフォルダ以下のファイル一覧
    docs_refs = "\n".join(
        f"docs-{index + 1}. {path.as_posix()}"
        for index, path in enumerate(inputs["docs"])
    )
    # srcフォルダ以下のファイル一覧
    src_refs = "\n".join(
        f"src-{index + 1}. {path.as_posix()}"
        for index, path in enumerate(inputs["src"])
    )
    # 指示プロンプトファイル出力先
    output_dir_text = str(output_dir.resolve())
    index_output_dir_text = str((output_dir.parent).resolve())

    # ドキュメント生成指示プロンプトを返す
    return f"""GitHub Copilot として、このリポジトリを対象に作業してください。

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
- 生成した Markdown 文書(architecture.mdなど)は、次のディレクトリに保存してください: {output_dir_text}
- ただし、`index.md` は docs 配下の入り口ページとして扱い、保存先は {index_output_dir_text} の直下にしてください
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
{docs_refs}

[src]
{src_refs}
""".strip()

def write_prompt_to_file(prompt: str, output_dir: Path) -> dict[str, Path]:
    """
    prompt を output_dir/docs_generation_prompt.mdとして保存する
    
    Parameters
    ----------
    prompt : str
        参考ファイルのパスリスト
    output_dir : Path
        指示プロンプトファイルの出力パス
    
    Returns
    -------        
    dict[str, list[Path]]
        参考ファイルのパスリスト
    """

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "docs_generation_prompt.md"
    output_path.write_text(prompt,encoding="utf-8")
    return { "prompt": output_path }

def parse_args(argv=None) -> argparse.Namespace:
    """
    コマンドライン引数を解析する
    """
    parser = argparse.ArgumentParser(
        description="プロジェクト分析に基づいて設計ドキュメント生成用 prompt を出力する"
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=None,
        help="対象プロジェクトのルートパス。未指定時はカレントディレクトリをルートパスを使用する"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("docs/reference"),
        help="生成される設計ドキュメントの保存先ディレクトリ",
    )
    parser.add_argument(
        "--prompt-output-dir",
        type=Path,
        default=Path("docs/prompts"),
        help="生成用 prompt ファイルの保存先ディレクトリ"
    )
    return parser.parse_args(argv)

def main(argv=None) -> None:
    """
    メイン関数
    """
    args = parse_args(argv)

    project_root = resolve_project_root(args.project_root)
    docs_output_dir = project_root / args.output_dir
    prompt_output_dir = project_root / args.prompt_output_dir

    inputs = collect_project_inputs(project_root)
    prompt = build_docs_generation_prompt(inputs, docs_output_dir)
    result = write_prompt_to_file(prompt, prompt_output_dir)

    print(f"prompt を {result['prompt']} に保存しました")
    print(f"生成ドキュメントの保存先: {docs_output_dir}")
    print()
    print(prompt)

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
