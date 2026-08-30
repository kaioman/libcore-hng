import os
import sys
import shutil
import subprocess
from pathlib import Path
from libcore_hng.cli.docs_prompt import (
    build_docs_generation_prompt, 
    collect_project_inputs, 
    write_prompt_to_file
)

def test_collect_project_inputs_returns_expected_files(tmp_path: Path) -> None:
    """
    doc と srcの構成を持つ一時ディレクトリから、対象ファイルを正しく収集できるか確認する
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

    result = collect_project_inputs(base_dir)
    print(result)

    assert [p.name for p in result["docs"]] == ["architecture.md"]
    assert [p.name for p in result["src"]] == ["sample.py"]

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
    prompt = build_docs_generation_prompt(
        {"docs": [architecture_md], "src": [sample_src_py]},
        output_dir
    )

    assert str(output_dir.resolve()) in prompt
    assert "/reference/reference" not in prompt

def test_write_prompt_to_file_creates_prompt_file(tmp_path: Path) -> None:
    """
    プロンプト本文を指定ディレクトリへ書き出し、ファイル名と内容が正しいか確認する
    """
    base_dir = tmp_path / "debug_generated-docs"
    docs_dir = base_dir / "docs"
    docs_dir.mkdir(parents=True)
    output_dir = base_dir / "docs" / "reference"
    result = write_prompt_to_file("prompt_body", output_dir)

    assert result["prompt"].exists()
    assert result["prompt"].name == "docs_generation_prompt.md"
    assert result["prompt"].read_text(encoding="utf-8") == "prompt_body"

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

    output_dir = project_copy / "docs" / "prompts"
    prompt_path = output_dir / "docs_generation_prompt.md"

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
            "docs/prompts",
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
    assert "生成対象:" in prompt_text
    assert "overview.md" in prompt_text
    assert "docs-" in prompt_text
    assert "src-" in prompt_text
