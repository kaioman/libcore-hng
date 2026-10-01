from pathlib import Path
from libcore_hng.cli.readme_prompt import(
    build_readme_prompt,
    main,
)

def test_build_readme_prompt_update_includes_existing_inputs(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    docs_dir = project_root / "docs"
    src_dir = project_root / "src"
    docs_dir.mkdir(parents=True)
    src_dir.mkdir(parents=True)
    readme_path = project_root / "README.md"
    pyproject_path = project_root / "pyproject.toml"
    architecturemd_path = docs_dir / "architecture.md"
    mainpy_path = src_dir / "main.py"

    readme_path.write_text("# Existing README", encoding="utf-8")
    pyproject_path.write_text('[project.scripts]\nreadme-prompt = "libcore-hng.cli.readme_prompt:main\n"', encoding="utf-8")
    architecturemd_path.write_text("# Architecture", encoding="utf-8")
    mainpy_path.write_text("print('hello')", encoding="utf-8")

    prompt = build_readme_prompt(project_root, mode="update")

    assert "【モード: 既存README更新】" in prompt
    assert "# Existing README" in prompt
    assert "readme-prompt" in prompt
    assert "# Architecture" in prompt
    assert "print('hello')" in prompt

def test_build_readme_prompt_generate_does_not_require_readme(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    src_dir = project_root / "src"
    src_dir.mkdir(parents=True)

    mainpy_path = src_dir / "main.py"
    mainpy_path.write_text("print('hello')", encoding="utf-8")

    prompt = build_readme_prompt(project_root, mode="generate")

    assert "【モード: 新規生成】" in prompt
    assert "README.md を新規作成してください" in prompt
    assert "README.md はまだ存在しません" in prompt
    assert "print('hello')" in prompt

def test_build_readme_prompt_without_pyproject_is_supported(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    project_root.mkdir(parents=True)

    prompt = build_readme_prompt(project_root, mode="generate")

    assert "pyproject.toml はありません。" in prompt

def test_readme_prompt_main_writes_prompt_file(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    project_root.mkdir(parents=True)

    result = main([
        "--project-root",
        str(project_root),
        "--mode",
        "generate",
        "--prompt-output-dir",
        "generated-prompts",
    ])

    prompt_path = project_root / "generated-prompts" / "docs_readme_prompt.md"
    
    assert result == 0
    assert prompt_path.exists()
    assert "【モード: 新規生成】" in prompt_path.read_text(encoding="utf-8")
