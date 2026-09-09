import os
import sys
import shutil
import subprocess
import pytest
from pathlib import Path
from libcore_hng.cli.docs_prompt import (
    build_docs_generation_prompt, 
    build_docs_update_prompt,
    collect_project_inputs_with_content, 
    MAX_SOURCE_FILE_CHARS,
    MAX_SOURCE_CONTENT_CHARS,
    parse_args,
    write_prompt_to_file
)
from libcore_hng.models.doc_types import FileContent

def test_collect_project_inputs_with_content_returns_expected_files_in_generate_mode(tmp_path: Path) -> None:
    """
    generateモードで doc と srcのファイルが正しく収集されることを確認する
    対象ファイルをパスのみで返すことを確認する
    """
    base_dir = tmp_path / "debug_generated-docs"
    docs_dir = base_dir / "docs"
    src_dir = base_dir / "src"
    docs_dir.mkdir(parents=True)
    src_dir.mkdir(parents=True)

    architecture_md = docs_dir / "architecture.md"
    sample_src_py = src_dir / "sample.py"
    architecture_md.write_text("# architecture", encoding="utf-8")
    sample_src_py.write_text("VALUE = 1\n", encoding="utf-8")

    result = collect_project_inputs_with_content(base_dir, mode="generate")

    assert [f["path"].name for f in result["docs"]] == ["architecture.md"]
    assert [f["path"].name for f in result["src"]] == ["sample.py"]
    assert result["docs"][0]["content"] == ""
    #assert result["src"][0]["content"] == "VALUE = 1\n"
    assert result["src"][0]["content"] == ""

def test_collect_project_inputs_with_content_reads_content_in_update_mode(tmp_path: Path) -> None:
    """
    updateモードで doc と srcのファイルの内容が正しく読み込まれることを確認する
    """
    base_dir = tmp_path / "debug_generated-docs"
    docs_dir = base_dir / "docs"
    src_dir = base_dir / "src"
    docs_dir.mkdir(parents=True)
    src_dir.mkdir(parents=True)

    architecture_md = docs_dir / "architecture.md"
    sample_src_py = src_dir / "sample.py"
    architecture_md.write_text("# architecture", encoding="utf-8")
    sample_src_py.write_text("VALUE = 1\n", encoding="utf-8")

    result = collect_project_inputs_with_content(base_dir, mode="update")

    assert [f["path"].name for f in result["docs"]] == ["architecture.md"]
    assert [f["path"].name for f in result["src"]] == ["sample.py"]
    assert result["docs"][0]["content"] == "# architecture"
    assert result["src"][0]["content"] == "VALUE = 1\n"

def test_collect_project_inputs_excludes_prompt_directory(tmp_path: Path) -> None:
    """
    docs/prompts 配下のMarkdownファイルが収集対象外になることを確認する
    """
    base_dir = tmp_path / "project"
    docs_dir = base_dir / "docs"
    src_dir = base_dir / "src"
    prompts_dir = docs_dir / "prompts"
    docs_dir.mkdir(parents=True)
    src_dir.mkdir(parents=True)
    prompts_dir.mkdir(parents=True)

    included_doc = docs_dir / "architecture.md"
    prompt_file = prompts_dir / "docs_generate_prompt.md"
    included_src = src_dir / "sample.py"
    included_doc.write_text("# architecture", encoding="utf-8")
    prompt_file.write_text("# prompt", encoding="utf-8")
    included_src.write_text("VALUE = 1\n", encoding="utf-8")

    # collect_project_inputs_with_contentを呼び出す
    result = collect_project_inputs_with_content(base_dir, mode="generate")

    assert [f["path"].name for f in result["docs"]] == ["architecture.md"]
    assert all(f["path"] != prompt_file for f in result["docs"])

def test_collect_project_inputs_excludes_custom_directory(tmp_path: Path) -> None:
    """
    指定されたディレクトリ配下のMarkdownファイルが収集対象外になることを確認する
    """
    base_dir = tmp_path / "project"
    docs_dir = base_dir / "docs"
    excluded_dir = docs_dir / "prompts"
    docs_dir.mkdir(parents=True)
    excluded_dir.mkdir(parents=True)

    included_doc = docs_dir / "architecture.md"
    excluded_doc = excluded_dir / "generated.md"
    included_doc.write_text("# architecture", encoding="utf-8")
    excluded_doc.write_text("# generated", encoding="utf-8")

    # collect_project_inputs_with_contentを呼び出す
    result = collect_project_inputs_with_content(
        base_dir, 
        mode="generate",
        excluded_dirs=[excluded_dir],
    )

    assert [f["path"].name for f in result["docs"]] == ["architecture.md"]

def test_collect_project_inputs_excludes_files_that_fail_to_read(
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch
    ) -> None:
    """
    読み込みに失敗したdocsとsrcのファイルが収集対象外になることを確認する
    """
    base_dir = tmp_path / "project"
    docs_dir = base_dir / "docs"
    src_dir = base_dir / "src"
    docs_dir.mkdir(parents=True)
    src_dir.mkdir(parents=True)

    unreadable_doc = docs_dir / "unreadable.md"
    readable_doc = docs_dir / "readable.md"
    unreadable_src = src_dir / "unreadable.py"
    readable_src = src_dir / "readable.py"
    unreadable_doc.write_text("# unreadable", encoding="utf-8")
    readable_doc.write_text("# readable", encoding="utf-8")
    unreadable_src.write_text("VALUE = 0\n", encoding="utf-8")
    readable_src.write_text("VALUE = 1\n", encoding="utf-8")

    original_read_text = Path.read_text

    def read_text_with_failure(path: Path, *args, **kwargs) -> str:
        if path in {unreadable_doc, unreadable_src}:
            raise OSError("test read failure")
        return original_read_text(path, *args, **kwargs)

    # 読み込みに失敗するようにモック
    monkeypatch.setattr(Path, "read_text", read_text_with_failure)

    # collect_project_inputs_with_contentを呼び出す
    result = collect_project_inputs_with_content(base_dir, mode="update")

    assert [f["path"].name for f in result["docs"]] == ["readable.md"]
    assert [f["path"].name for f in result["src"]] == ["readable.py"]

def test_collect_project_inputs_rejects_invalid_mode(tmp_path: Path) -> None:
    """
    無効なモードが指定された場合に例外が発生することを確認する
    """
    with pytest.raises(ValueError, match="generate.*update"):
        collect_project_inputs_with_content(tmp_path, mode="invalid")

def test_build_docs_generation_prompt_uses_output_dir_without_duplicate_reference(tmp_path: Path) -> None:
    """
    生成用プロンプトの出力先が重複せず、正しいディレクトリが本文に含まれるか確認する
    """
    base_dir = tmp_path / "debug_generated-docs"
    docs_dir = base_dir / "docs"
    src_dir = base_dir / "src"
    docs_dir.mkdir(parents=True)
    src_dir.mkdir(parents=True)

    architecture_md = docs_dir / "architecture.md"
    sample_src_py = src_dir / "sample.py"
    architecture_md.write_text("# architecture", encoding="utf-8")
    sample_src_py.write_text("VALUE = 1\n", encoding="utf-8")

    output_dir = base_dir / "docs" / "reference"
    inputs = {
        "docs": [FileContent(path=architecture_md, content="# architecture")], 
        "src": [FileContent(path=sample_src_py, content="VALUE = 1\n")]
    }
    prompt = build_docs_generation_prompt(inputs, output_dir)

    assert str(output_dir.resolve()) in prompt
    assert "/reference/reference" not in prompt
    assert "【モード: 新規生成】" in prompt

def test_write_prompt_to_file_creates_prompt_file(tmp_path: Path) -> None:
    """
    プロンプト本文を指定ディレクトリへ書き出し、ファイル名と内容が正しいか確認する
    """
    base_dir = tmp_path / "debug_generated-docs"
    docs_dir = base_dir / "docs"
    docs_dir.mkdir(parents=True)
    output_dir = base_dir / "docs" / "reference"
    result = write_prompt_to_file("prompt_body", output_dir, mode="generate")

    assert result["prompt"].exists()
    assert result["prompt"].name == "docs_generate_prompt.md"
    assert result["prompt"].read_text(encoding="utf-8") == "prompt_body"

def test_build_docs_update_prompt_includes_existing_content(tmp_path: Path) -> None:
    """
    update モード用プロンプトが既存ドキュメント内容を含むことを確認する
    """
    base_dir = tmp_path / "debug_generated-docs"
    docs_dir = base_dir / "docs"
    src_dir = base_dir / "src"
    docs_dir.mkdir(parents=True)
    src_dir.mkdir(parents=True)

    architecture_md = docs_dir / "architecture.md"
    sample_src_py = src_dir / "sample.py"
    doc_content = "# 既存のアーキテクチャ設計"
    src_content = "def sample(): pass\n"
    architecture_md.write_text(doc_content, encoding="utf-8")
    sample_src_py.write_text(src_content, encoding="utf-8")

    output_dir = base_dir / "docs" / "reference"
    inputs = {
        "docs": [FileContent(path=architecture_md, content=doc_content)], 
        "src": [FileContent(path=sample_src_py, content=src_content)]
    }
    prompt = build_docs_update_prompt(inputs, output_dir)

    assert "【モード: 既存ドキュメント更新】" in prompt
    assert doc_content in prompt
    assert "sample.py" in prompt
    assert "差分のみ" in prompt

def test_docs_prompt_generates_prompt_for_repo_root(tmp_path: Path) -> None:
    """
    CLI を実行し、実プロジェクトのコピー先で docs_generation_prompt.md が生成されることを確認する
    """
    repo_root = Path(__file__).resolve().parents[2]
    project_copy = tmp_path / "libcore-hng-copy"

    # 本リポジトリを一時ディレクトリに複製してテスト内で安全に実行する
    shutil.copytree(
        repo_root, 
        project_copy, 
        ignore=shutil.ignore_patterns(
            ".git", 
            "__pycache__", 
            ".pytest_cache",
            "env",
            "logs",
        )
    )

    # プロンプト生成ファイルの出力先ディレクトリ
    prompt_output_dir = project_copy / "docs" / "prompts"
    # 生成ドキュメントの出力先ディレクトリ
    docs_output_dir = project_copy / "docs" / "reference"
    # プロンプト生成ファイルのパス
    prompt_path = prompt_output_dir / "docs_generate_prompt.md"

    env = os.environ.copy()
    src_path = str(project_copy / "src")
    if env.get("PYTHONPATH"):
        env["PYTHONPATH"] = src_path + os.pathsep + env["PYTHONPATH"]
    else:
        env["PYTHONPATH"] = src_path
    
    result = subprocess.run(
        [
            sys.executable, 
            "-m", 
            "libcore_hng.cli.docs_prompt", 
            "--project-root", 
            str(project_copy),
            "--output-dir",
            "docs/reference",
            "--prompt-output-dir",
            "docs/prompts",
            "--mode",
            "generate",
        ],
        cwd=str(project_copy),
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )

    assert prompt_path.exists(), result.stdout
    prompt_text = prompt_path.read_text(encoding="utf-8")

    assert "GitHub Copilot として" in prompt_text
    assert "【モード: 新規生成】" in prompt_text
    assert "生成対象:" in prompt_text
    assert "overview.md" in prompt_text
    assert str(docs_output_dir.resolve()) in prompt_text
    assert "docs-" in prompt_text
    assert "source-" in prompt_text

def test_collect_project_inputs_uses_custom_source_dirs_and_extentsions(tmp_path: Path) -> None:
    """
    source_dirs と source_extensions で、対象ソース収集範囲が拡張できることを確認
    """
    base_dir = tmp_path / "project"
    app_dir = base_dir / "app"
    legacy_dir = base_dir / "legacy"
    app_dir.mkdir(parents=True)
    legacy_dir.mkdir(parents=True)

    (app_dir / "main.py").write_text("print('keep')\n", encoding="utf-8")
    (legacy_dir / "legacy.ts").write_text("export const value = 1\n", encoding="utf-8")
    (legacy_dir / "notes.txt").write_text("ignore me\n", encoding="utf-8")

    result = collect_project_inputs_with_content(
        base_dir,
        mode="generate",
        source_dirs=["app", "legacy"],
        source_extensions=[".py", ".ts"],
    )

    collected = {file["path"].name for file in result["src"]}
    assert collected == {"main.py", "legacy.ts"}

def test_collect_project_inputs_excludes_default_directory_names(tmp_path: Path) -> None:
    """
    DEFAULT_EXCLUDED_DIRS に含まれるディレクトリは収集対象外になることを確認
    """
    base_dir = tmp_path / "project"
    src_dir = base_dir / "src"
    node_modules_dir = base_dir / "node_modules"
    src_dir.mkdir(parents=True)
    node_modules_dir.mkdir(parents=True)

    kept = src_dir / "keep.py"
    excluded = node_modules_dir / "ignored.js"
    kept.write_text("print('keep')\n", encoding="utf-8")
    excluded.write_text("console.log('skip')\n", encoding="utf-8")

    result = collect_project_inputs_with_content(
        base_dir,
        mode="generate"
    )

    assert [file["path"].name for file in result["src"]] == ["keep.py"]
    assert all(file["path"] != excluded for file in result["src"])

def test_parse_args_supports_multiple_source_dirs_and_extensions() -> None:
    """
    --source-dir と --source-ext の複数指定が argparse で正しく解釈されるか確認
    """
    args = parse_args([
        "--source-dir", "src", "app",
        "--source-ext", ".py", ".ts",
    ])

    assert args.source_dir == [Path("src"), Path("app")]
    assert args.source_ext == [".py", ".ts"]

def test_build_docs_update_prompt_truncates_large_source_input(tmp_path: Path) -> None:
    """
    update モードで巨大ソース入力が上限に達した場合に、切り詰め通知が含まれることを確認
    """
    base_dir = tmp_path / "debug_generated-docs"
    docs_dir = base_dir / "docs"
    src_dir = base_dir / "src"
    docs_dir.mkdir(parents=True)
    src_dir.mkdir(parents=True)

    doc_file = docs_dir / "architecture.md"
    doc_file.write_text("# architecture\n", encoding="utf-8")
    long_source = "x" * (MAX_SOURCE_FILE_CHARS * 2)
    source_file = src_dir / "large.py"
    source_file.write_text(long_source, encoding="utf-8")

    inputs = {
        "docs": [FileContent(path=doc_file, content="# architecture\n")],
        "src": [FileContent(path=source_file, content=long_source)]        
    }

    prompt = build_docs_update_prompt(inputs, base_dir / "docs" / "reference")

    assert "切り詰めています" in prompt
    assert source_file.name in prompt
    assert len(prompt) < MAX_SOURCE_FILE_CHARS * 10
