import libcore_hng.utils.crypto as crypto
from pathlib import Path
from cryptography.fernet import Fernet
from libcore_hng.cli import encrypt_file

def test_run_encrypt_file_with_generated_key(tmp_path: Path, monkeypatch, capsys) -> None:
    """
    秘密鍵未指定時のファイル暗号化処理(出力先未指定)
    """
    source_path = tmp_path / "sample.json"
    source_data = b'{"name": "sample"}'
    source_path.write_bytes(source_data)

    generated_key = Fernet.generate_key()
    monkeypatch.setattr(
        crypto,
        "generate_key",
        lambda: generated_key,
    )
    monkeypatch.setattr(
        encrypt_file.getpass,
        "getpass",
        lambda _: "",
    )

    result = encrypt_file.run(str(source_path), None)

    output_path = tmp_path / "sample.json.enc"

    assert result == 0
    assert output_path.is_file()
    assert Fernet(generated_key).decrypt(
        output_path.read_bytes()
    ) == source_data
    # コンソールに生成された秘密鍵が表示されたか検証
    assert generated_key.decode("utf-8") in capsys.readouterr().out

def test_run_encrypts_file_with_specified_key_and_output(tmp_path: Path, monkeypatch, capsys) -> None:
    """
    秘密鍵指定時のファイル暗号化処理(出力先指定)
    """
    source_path = tmp_path / "sample.json"
    output_path = tmp_path / "encrypted" / "sample.enc"
    source_data = b'{"name": "sample"}'
    source_path.write_bytes(source_data)
    output_path.parent.mkdir()

    secret_key = Fernet.generate_key().decode("utf-8")
    monkeypatch.setattr(
        encrypt_file.getpass,
        "getpass",
        lambda _: secret_key,
    )

    result = encrypt_file.run(
        str(source_path),
        str(output_path),
    )
    captured = capsys.readouterr().out

    assert secret_key not in captured
    assert result == 0
    assert output_path.is_file()
    assert Fernet(secret_key.encode("utf-8")).decrypt(
        output_path.read_bytes()
    ) == source_data

def test_run_returns_error_for_missing_source_file(tmp_path: Path, monkeypatch) -> None:
    """
    入力パスが不正な場合に秘密鍵の入力を要求しないことの確認
    """
    source_path = tmp_path / "missing.json"

    def fail_if_prompted(_: str) -> str:
        raise AssertionError("秘密鍵の入力を求めてはいけません")

    monkeypatch.setattr(
        encrypt_file.getpass,
        "getpass",
        fail_if_prompted,
    )

    result = encrypt_file.run(str(source_path), None)

    assert result == 1

def test_run_rejects_same_source_and_output_path(tmp_path: Path, monkeypatch) -> None:
    """
    入力パスと出力パスが同一の場合に秘密鍵の入力を要求しないことの確認
    """
    source_path = tmp_path / "sample.json"
    source_path.write_text("sample", encoding="utf-8")

    def fail_if_prompted(_: str) -> str:
        raise AssertionError("秘密鍵の入力を求めてはいけません")

    monkeypatch.setattr(
        encrypt_file.getpass,
        "getpass",
        fail_if_prompted,
    )

    result = encrypt_file.run(
        str(source_path),
        str(source_path),
    )

    assert result == 1

def test_run_returns_error_for_missing_output_directory(tmp_path: Path, monkeypatch) -> None:
    """
    出力先ディレクトリが存在しない場合に秘密鍵の入力を要求しないことの確認
    """
    source_path = tmp_path / "sample.json"
    output_path = tmp_path / "missing" / "sample.enc"
    source_path.write_text("sample", encoding="utf-8")

    def fail_if_prompted(_: str) -> str:
        raise AssertionError("秘密鍵の入力を求めてはいけません")

    monkeypatch.setattr(
        encrypt_file.getpass,
        "getpass",
        fail_if_prompted,
    )

    result = encrypt_file.run(
        str(source_path),
        str(output_path),
    )

    assert result == 1
