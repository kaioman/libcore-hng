from __future__ import annotations

import argparse
from pathlib import Path
from typing import Literal
from libcore_hng.models.doc_types import FileContent, ProjectInputs, DocGaps

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

def collect_project_inputs_with_content(
        project_root: str | Path | None,
        mode: Literal["generate", "update"] = "generate",
        excluded_dirs: list[str | Path] | None = None
    ) -> ProjectInputs:
    """
    プロジェクトの docs と src のファイルを収集する

    Parameters
    ----------
    project_root : str | Path | None
        プロジェクトルートパス
    mode : Literal["generate", "update"], optional
        処理モード ("generate" または "update")
    excluded_dirs : list[str | Path] | None, optional
        除外するディレクトリのリスト

    Returns
    -------
    ProjectInputs
        参考ファイルの内容を保持するオブジェクト
        docsフォルダ、srcフォルダ別に保持する
    """

    # ルートパスを取得する
    base_root = Path(project_root).resolve() if project_root else Path.cwd().resolve()

    # モードの検証
    if mode not in ("generate", "update"):
        raise ValueError(
            f"不正なモード: {mode}. 'generate' または 'update' を指定してください。"
        )

    # docsフォルダルート
    docs_root = base_root / "docs"
    # srcフォルダルート
    src_root = base_root / "src"

    # 除外ディレクトリの解決
    excluded_roots = {(docs_root / "prompts").resolve()}
    for excluded_dir in excluded_dirs or []:
        excluded_path = Path(excluded_dir).resolve()
        if not excluded_path.is_absolute():
            excluded_path = base_root / excluded_path
        excluded_roots.add(excluded_path.resolve())
    
    # docs と src のファイルを収集するためのリストを初期化
    docs_files: list[FileContent] = []
    src_files: list[FileContent] = []

    # docs ファイル収集
    if docs_root.exists():
        for doc_path in sorted(docs_root.rglob("*.md")):
            # 除外ディレクトリに含まれる場合はスキップ
            if any(
                excluded_root in doc_path.resolve().parents 
                for excluded_root in excluded_roots
            ):
                continue
            
            if mode == "update":
                if doc_path.is_file():
                    try:
                        content = doc_path.read_text(encoding="utf-8")
                        docs_files.append(FileContent(path=doc_path, content=content))
                    except (OSError, UnicodeDecodeError):
                        continue
            else:
                docs_files.append(FileContent(path=doc_path, content=""))  # contentは空で収集

    # src ファイル収集
    if src_root.exists():
        for src_path in sorted(src_root.rglob("*.py")):
            # 除外ディレクトリに含まれる場合はスキップ
            if any(
                excluded_root in src_path.resolve().parents
                for excluded_root in excluded_roots
            ):
                continue

            if src_path.is_file():
                try:
                    content = src_path.read_text(encoding="utf-8")
                    src_files.append(FileContent(path=src_path, content=content))
                except (OSError, UnicodeDecodeError):
                    continue

    # 取得結果を返す
    return {
        "docs": docs_files,
        "src": src_files,
    }

def build_docs_generation_prompt(inputs: ProjectInputs, output_dir: Path) -> str:
    """
    ドキュメント生成用のプロンプトを構築する(1から生成)

    Parameters
    ----------
    inputs : ProjectInputs
        参考ファイルの内容を保持するオブジェクト
    output_dir : Path
        指示プロンプトファイルの出力先パス
    
    Returns
    -------
    str
        ドキュメント生成指示プロンプト
    """
    # docsフォルダ以下のファイル一覧
    docs_refs = "\n".join(
        f"docs-{index + 1}. {file['path'].as_posix()}"
        for index, file in enumerate(inputs["docs"])
    )
    # srcフォルダ以下のファイル一覧
    src_refs = "\n".join(
        f"src-{index + 1}. {file['path'].as_posix()}"
        for index, file in enumerate(inputs["src"])
    )
    # 指示プロンプトファイル出力先
    output_dir_text = str(output_dir.resolve())
    index_output_dir_text = str(output_dir.parent.resolve())
        
    # ドキュメント生成指示プロンプトを返す
    return f"""GitHub Copilot として、このリポジトリを対象に作業してください。

【モード: 新規生成】

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

def build_docs_update_prompt(inputs: ProjectInputs, output_dir: Path) -> str:
    """
    ドキュメント更新用のプロンプトを構築する

    Parameters
    ----------
    inputs : ProjectInputs
        参考ファイルの内容を保持するオブジェクト
    output_dir : Path
        指示プロンプトファイルの出力先パス
    
    Returns
    -------
    str
        ドキュメント更新指示プロンプト
    """
    # docsフォルダ以下のファイル一覧
    existing_docs_refs = "\n".join(
        f"--- {file['path'].name} ---\n{file['content']}"
        for file in inputs["docs"] if file["content"]
    ) if inputs["docs"] else "docsフォルダに既存のドキュメントは存在しません。"

    # srcフォルダ以下のファイル一覧
    src_refs = "\n".join(
        f"- {file['path'].as_posix()}"
        for file in inputs["src"]
    )

    # 指示プロンプトファイル出力先
    output_dir_text = str(output_dir.resolve())
    index_output_dir_text = str(output_dir.parent.resolve())
        
    # 既存ドキュメント更新指示プロンプトを返す
    return f"""GitHub Copilot として、このリポジトリを対象に作業してください。

【モード: 既存ドキュメント更新】

既存の設計ドキュメント群と現在のソースコード実装を照合し、
以下のドキュメントの**差分のみ**を修正・更新してください。

対象ドキュメント:
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
- **既存ドキュメント全体を上書きするのではなく、差分部分のみを修正してください**
- 不整合があれば、該当セクションのみを修正して出力してください
- 修正が不要なセクションは出力に含めないでください
- 設計変更が必要な場合は、その旨を明記してください
- 既存の優れた説明は保持し、古い情報のみ更新してください
- 修正内容には修正理由を簡潔に記載してください
- `src` のファイルは修正対象ではなく、分析用の参考入力です

修正対象は以下の出力先ディレクトリに保存してください: {output_dir_text}
（`index.md` は {index_output_dir_text} の直下）

禁止事項:
- ドキュメント全体の再生成（差分のみ）
- src配下の編集
- ソースコード修正
- 設定ファイル編集

許可事項:
- ドキュメント参考入力の確認
- 差分修正の出力
- Markdown形式での更新情報提供

【既存ドキュメント】
{existing_docs_refs}

【現在のソースコード構成】
{src_refs}
""".strip()

def write_prompt_to_file(prompt: str, output_dir: Path, mode: Literal["generate", "update"]) -> dict[str, Path]:
    """
    prompt を output_dir に保存する
    
    Parameters
    ----------
    prompt : str
        参考ファイルのパスリスト
    output_dir : Path
        指示プロンプトファイルの出力パス
    mode : Literal["generate", "update"]
        モード（"generate" または "update"）

    Returns
    -------        
    dict[str, Path]
        参考ファイルのパスリスト
    """

    # output_dir が存在しない場合は作成する
    output_dir.mkdir(parents=True, exist_ok=True)

    # プロンプトファイル名を決定する
    prompt_filename = f"docs_{mode}_prompt.md"
    # プロンプトファイルのパスを決定する
    output_path = output_dir / prompt_filename
    # プロンプトをファイルに書き込む
    output_path.write_text(prompt, encoding="utf-8")

    # 生成結果を返す
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
        "--mode",
        type=str,
        choices=["generate", "update"],
        default="generate",
        help="実行モード: generate=1から生成, update=既存ドキュメント更新",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("docs/reference"),
        help="生成される設計ドキュメントの保存先ディレクトリ"
    )
    parser.add_argument(
        "--prompt-output-dir",
        type=Path,
        default=Path("docs/prompts"),
        help="生成用 prompt ファイルの保存先ディレクトリ"
    )
    return parser.parse_args(argv)

def main(argv=None) -> int:
    """
    メイン関数
    """

    # コマンドライン引数解析
    args = parse_args(argv)

    # ルートパスを解決
    project_root = resolve_project_root(args.project_root)
    # 出力先ディレクトリを解決
    docs_output_dir = project_root / args.output_dir
    # prompt 出力先ディレクトリを解決
    prompt_output_dir = project_root / args.prompt_output_dir

    # モードに応じた入力収集
    inputs = collect_project_inputs_with_content(
        project_root, 
        mode=args.mode,
        excluded_dirs=[prompt_output_dir],
    )

    # プロンプト生成
    if args.mode == "generate":
        prompt = build_docs_generation_prompt(inputs, docs_output_dir)
    elif args.mode == "update":
        prompt = build_docs_update_prompt(inputs, docs_output_dir)
    else:
        raise ValueError(f"不正なモード: {args.mode}")

    # ファイル出力
    result = write_prompt_to_file(prompt, prompt_output_dir, args.mode)

    # 結果表示
    print(f"[{args.mode.upper()}モード] prompt を {result['prompt']} に保存しました")
    print(f"生成ドキュメントの保存先: {docs_output_dir}")
    print()
    print(prompt)

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
