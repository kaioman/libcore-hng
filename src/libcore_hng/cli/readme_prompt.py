from __future__ import annotations

import argparse
from pathlib import Path
from libcore_hng.cli.docs_prompt import (
    MAX_SOURCE_CONTENT_CHARS,
    MAX_SOURCE_FILE_CHARS,
    collect_project_inputs_with_content,
    resolve_project_root,
    write_prompt_to_file
)
from libcore_hng.models.doc_types import FileContent

def parse_args(argv=None) -> argparse.Namespace:
    """
    コマンドライン引数を解析する
    """
    parser = argparse.ArgumentParser(
        description="README更新用の指示プロンプトを生成する"
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=None,
        help="対象プロジェクトのルートパス。未指定時はカレントディレクトリを使用",
    )
    parser.add_argument(
        "--mode",
        type=str,
        choices=["generate", "update"],
        default="update",
        help="README生成モード： generate=新規作成, update=既存README差分更新",
    )
    parser.add_argument(
        "--source-dir",
        type=Path,
        nargs="+",
        default=None,
        help="README分析対象のソースコードディレクトリ。複数指定可能",
    )
    parser.add_argument(
        "--source-ext",
        nargs="+",
        default=None,
        help="収集対象の拡張子。複数指定可能",
    )
    parser.add_argument(
        "--prompt-output-dir",
        type=Path,
        default=Path("docs/prompts"),
        help="生成した README 用 prompt の保存先ディレクトリ",
    )
    return parser.parse_args(argv)

def read_prompt_input(path: Path) -> str:
    """
    指定されたパスのファイルを UTF-8 で読み込み、文字列として返す。

    Parameters
    ----------
    path : Path
        読み込むファイルのパス 

    Returns
    -------
    str
        ファイルの内容を文字列として返す   
    """
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise ValueError(f"入力ファイルを読み込めません: {path}") from exc

def format_reference_files(files: list[FileContent], label: str, max_chars: int) -> tuple[str, int]:
    """
    参照ファイルの内容を指定された文字数制限内でフォーマットし、文字列として返す。
    
    Parameters
    ----------
    files : list[FileContent]
        参照するファイルのリスト。各要素は辞書で、'path' と 'content' キーを持つ。  
    label : str
        参照ファイルのラベル
    max_chars : int
        フォーマット後の文字数制限

    Returns
    -------
    tuple[str, int]
        フォーマットされた参照ファイルの文字列と、使用した文字数のタプル
    """
    references: list[str] = []
    total_chars = 0

    # 参照ファイルを順に処理
    for index, file in enumerate(files, start=1):
        # 参照ファイルのヘッダーと内容をフォーマット
        separator = "\n\n" if references else ""
        header = f"--- {label}-{index}: {file['path'].as_posix()} ---\n"
        remaining_chars = max_chars - total_chars - len(separator)
        content_chars = remaining_chars - len(header)

        # 内容が残り文字数を超える場合、ファイルを省略する
        if content_chars <= 0:
            omitted_count = len(files) - index + 1
            omitted_notice = (
                f"[入力サイズ上限により{omitted_count}ファイルを省略しました]"
            )
            if len(omitted_notice) <= remaining_chars:
                references.append(omitted_notice)
                total_chars += len(separator) + len(omitted_notice)
            break

        # ファイル内容を制限内で取得
        content = file["content"]
        content_limit = min(MAX_SOURCE_FILE_CHARS, content_chars)
        truncated = len(content) > content_limit
        truncation_notice = "\n[入力サイズ上限により内容を省略しました]"
        if truncated:
            if content_chars <= len(truncation_notice):
                omitted_count = len(files) - index + 1
                omitted_notice = (
                    f"[入力サイズ上限により{omitted_count}ファイルを省略しました]"
                )
                if len(omitted_notice) <= remaining_chars:
                    references.append(omitted_notice)
                    total_chars += len(separator) + len(omitted_notice)
                break
            content_limit -= len(truncation_notice)

        # フォーマットされた参照ファイルのエントリを作成
        entry = header + content[:content_limit]
        if truncated:
            entry += truncation_notice

        # 参照ファイルのエントリをリストに追加し、使用した文字数を更新
        references.append(entry)
        total_chars += len(separator) + len(entry)

    return "\n\n".join(references), total_chars

def build_readme_prompt(
    project_root: Path,
    mode: str,
    source_dirs: list[Path] | None = None,
    source_ext: list[str] | None = None,
) -> str:
    """
    README 更新用の指示プロンプトを生成する
    
    Parameters
    ----------
    project_root : Path
        プロジェクトのルートディレクトリのパス
    mode : str
        README 生成モード。'generate' または 'update' のいずれか
    source_dirs : list[Path] | None
        README 分析対象のソースコードディレクトリのリスト。未指定時はデフォルトディレクトリを使用
    source_ext : list[str] | None
        README 分析対象のソースコード拡張子のリスト。未指定時はデフォルト拡張子を使用
    
    Returns
    -------
    str
        README 更新用の指示プロンプト
    """

    # プロジェクトのdocsとソースファイルを収集する
    inputs = collect_project_inputs_with_content(
        project_root=project_root,
        mode="update",
        source_dirs=source_dirs,
        source_extensions=source_ext,
        excluded_dirs=[project_root / "docs" / "prompts"],
    )

    # README.mdファイルのパスを取得
    readme_path = project_root / "README.md"
    remaining_chars = MAX_SOURCE_CONTENT_CHARS
    existing_readme = ""
    # modeが更新モードかつREADME.mdファイルの存在有無を判定する
    if mode == "update" and readme_path.exists():
        # README.mdの内容と使用文字数を取得する
        existing_readme, userd_chars = format_reference_files(
            [{
                "path": readme_path,
                "content": read_prompt_input(readme_path),
            }],
            "README",
            remaining_chars,
        )
        remaining_chars -= userd_chars

    # pyproject.tomlのパスを取得
    pyproject_path = project_root / "pyproject.toml"
    pyproject_content = "pyproject.toml はありません。"
    if pyproject_path.is_file():
        # pyproject.tomlの内容と使用文字数を取得する
        pyproject_content, userd_chars = format_reference_files(
            [{
                "path": pyproject_path,
                "content": read_prompt_input(pyproject_path),
            }],
            "設定",
            remaining_chars,
        )
        remaining_chars -= userd_chars

    # docsフォルダの内容と使用文字数を収集する
    docs_refs, userd_chars = format_reference_files(
        inputs["docs"], "docs", remaining_chars
    )
    remaining_chars -= userd_chars

    # srcフォルダの内容と使用文字数を収集する
    source_refs, _ = format_reference_files(
        inputs["src"], "source", remaining_chars
    )

    # モード判定してmodeラベルとインストラクションを生成する
    if mode == "generate":
        mode_label = "新規生成"
        main_instruction = "現在のリポジトリ構成を分析して、README.md を新規作成してください。"
    else:
        mode_label = "既存README更新"
        main_instruction = (
            "既存の README.md と現在の実装を照合し、"
            "差分のみを修正してください"
        )

    return f"""GitHub Copilot として、このリポジトリを対象に作業してください。

【モード: {mode_label}】

{main_instruction}

対象:
- README.md
- 実装コード
- 主要な設計ドキュメント

要件:
- 出力は日本語で行ってください
- 文体はですます調にしてください
- Markdown 形式で出力してください
- README を読みやすく、プロジェクトの概要・利用方法・CLI・設計方針が伝わる内容にしてください
- 既存 README の良い説明は残し、古い情報や実装との不一致のみ更新してください
- 設計変更が必要な場合は、その旨を簡潔に記載してください
- README 自体の修正は、このプロンプトの出力に留めてください
- ソースコードの編集は行わず、README 更新用の指示内容を生成してください

禁止事項:
- ソースコード修正
- ドキュメントの全書き換え
- 参考入力ディレクトリ配下の編集
- 設定ファイル編集
- README の直接変更実行

【既存 README】
{existing_readme or "README.md はまだ存在しません。新規作成用の内容を生成してください。"}

【プロジェクト設定: pyproject.toml】
{pyproject_content}

【ドキュメント参照】
{docs_refs or "ドキュメント参照はありません。"}

【ソースコード参照】
{source_refs or "ソースコード参照はありません。"}
""".strip()

def main(argv=None) -> int:
    """
    メイン関数
    """

    # コマンドライン引数解析
    args = parse_args(argv)

    # ルートパスを解決
    project_root = resolve_project_root(args.project_root)
    # prompt 出力先ディレクトリを解決
    prompt_output_dir = project_root / args.prompt_output_dir

    # 生成用プロンプトを取得
    prompt = build_readme_prompt(
        project_root=project_root,
        mode=args.mode,
        source_dirs=args.source_dir,
        source_ext=args.source_ext,
    )

    # ファイル出力
    result = write_prompt_to_file(prompt, prompt_output_dir, "readme")

    # 結果表示
    print(f"[README {args.mode.upper()}モード] prompt を {result['prompt']} に保存しました")
    print(prompt)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
