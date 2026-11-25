from pathlib import Path
from libcore_hng.cli.directory_tree import main
from libcore_hng.utils.directory_tree import render_directory_tree

def test_tree_sorts_directories_first_and_excludes_matching_names(
    tmp_path: Path,
) -> None:
    root = tmp_path / "root"
    (root / "folder10").mkdir(parents=True)
    (root / "folder2").mkdir()
    (root / "folder2" / "omit").mkdir()
    (root / "omit").mkdir()
    (root / "file10.txt").touch()
    (root / "file2.txt").touch()

    output = render_directory_tree(root, excluded_dirs=["omit"])

    assert output.splitlines() == [
        "root",
        "├── folder2",
        "├── folder10",
        "├── file2.txt",
        "└── file10.txt",
    ]

def test_excel_format_emits_tab_separated_columns(tmp_path: Path) -> None:
    root = tmp_path / "root"
    root.mkdir()
    (root / "sample.txt").touch()

    output = render_directory_tree(root, output_format="excel")

    assert output.splitlines() == [
        "depth\ttype\tname\trelative_path",
        "0\tdirectory\troot\t.",
        "1\tfile\tsample.txt\tsample.txt",
    ]

def test_unknown_config_key_warns_and_uses_model_default(
    tmp_path: Path,
    capsys,
) -> None:
    root = tmp_path / "root"
    root.mkdir()
    (root / "sample.txt").touch()
    config_path = tmp_path / "directory-tree.json"
    config_path.write_text(
        '{"borders": {"normal": {"unknown": "??"}}}',
        encoding="utf-8",
    )

    result = main([str(root), "--config", str(config_path)])

    captured = capsys.readouterr()
    assert result == 0
    assert "└── sample.txt" in captured.out
    assert "unknown" in captured.err
    assert "既定値" in captured.err
