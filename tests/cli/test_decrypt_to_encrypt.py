import os
import subprocess
from pathlib import Path
import pytest
from libcore_hng.cli import decrypt_to_encrypt

def test_parse_args_does_not_accept_secret_key() -> None:
    args = decrypt_to_encrypt.parse_args(["sample.json.enc"])

    assert args.encrypt_file == "sample.json.enc"
    with pytest.raises(SystemExit):
        decrypt_to_encrypt.parse_args(
            ["--secret-key", "secret", "sample.json.enc"]
        )

def test_run_returns_error_without_prompting_for_missing_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    missing_flie = tmp_path / "missing.json.enc"

    def fail_if_prompted(prompt: str) -> str:
        pytest.fail("存在しないファイルでは秘密鍵を要求しないこと")

    monkeypatch.setattr(
        decrypt_to_encrypt.getpass,
        "getpass",
        fail_if_prompted,
    )

    assert decrypt_to_encrypt.run(None, str(missing_flie)) == 1

def test_run_prompts_without_echo_and_reencrypts_modified_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    encrypted_file = tmp_path / "sample.json.enc"
    encrypted_file.write_bytes(b"encrypted")
    secret_key = "test-secret-key"
    prompts: list[str] = []
    encryption_calls: list[tuple[str, str]] = []

    def get_secret(prompt: str) -> str:
        prompts.append(prompt)
        return secret_key

    def fake_decrypt(source_path: str, destinaion_path: str, key: str) -> None:
        assert source_path == str(encrypted_file)
        assert key == secret_key
        Path(destinaion_path).write_text("original", encoding="utf-8")

    def fake_notepad(command: list[str | Path], check: bool) -> None:
        assert command[0] == "notepad.exe"
        assert check is True

        decrypted_file = Path(command[1])
        decrypted_file.write_text("edited", encoding="utf-8")
        file_stat = decrypted_file.stat()
        os.utime(
            decrypted_file,
            ns=(
                file_stat.st_atime_ns,
                file_stat.st_mtime_ns + 2_000_000_000,
            ),
        )

    def fake_encrypt(source_path: str, destination_path: str, key: str) -> None:
        assert Path(source_path).read_text(encoding="utf-8") == "edited"
        encryption_calls.append((destination_path, key))

    monkeypatch.setattr(decrypt_to_encrypt.getpass, "getpass", get_secret)
    monkeypatch.setattr(decrypt_to_encrypt, "create_decryption_file", fake_decrypt)
    monkeypatch.setattr(decrypt_to_encrypt.subprocess, "run", fake_notepad)
    monkeypatch.setattr(decrypt_to_encrypt, "create_encryption_file", fake_encrypt)

    result = decrypt_to_encrypt.run(None, str(encrypted_file))
    captured = capsys.readouterr()

    assert result == 0
    assert prompts == ["秘密鍵を入力してください:"]
    assert secret_key not in captured.out
    assert secret_key not in captured.err
    assert encryption_calls == [(str(encrypted_file), secret_key)]

def test_run_returns_error_when_decryption_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    encrypted_file = tmp_path / "sample.json.enc"
    encrypted_file.write_bytes(b"encrypted")

    def fail_decrypt(source_path: str, destination_path: str, key: str) -> None:
        raise ValueError("decryption failed")

    monkeypatch.setattr(
        decrypt_to_encrypt,
        "create_decryption_file",
        fail_decrypt,
    )

    assert decrypt_to_encrypt.run("test-key", str(encrypted_file)) == 1

def test_run_returns_error_when_editor_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    encrypted_file = tmp_path / "sample.json.enc"
    encrypted_file.write_bytes(b"encrypted")

    def fake_decrypt(source_path: str, destination_path: str, key: str) -> None:
        Path(destination_path).write_text("original", encoding="utf-8")

    def fail_editor(command: list[str | Path], check: bool) -> None:
        raise subprocess.CalledProcessError(1, command)

    monkeypatch.setattr(decrypt_to_encrypt, "create_decryption_file", fake_decrypt)
    monkeypatch.setattr(decrypt_to_encrypt.subprocess, "run", fail_editor)

    assert decrypt_to_encrypt.run("test-key", str(encrypted_file)) == 1

def test_main_returns_run_exit_code(monkeypatch: pytest.MonkeyPatch) -> None:
    run_calls: list[tuple[str | None, str]] = []

    def fake_run(secret_key: str | None, encrypted_file: str) -> int:
        run_calls.append((secret_key, encrypted_file))
        return 1
    
    monkeypatch.setattr(decrypt_to_encrypt, "run", fake_run)

    result = decrypt_to_encrypt.main(["sample.json.enc"])

    assert result == 1
    assert run_calls == [(None, "sample.json.enc")]
