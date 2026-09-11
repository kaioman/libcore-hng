from pathlib import Path
from cryptography.fernet import Fernet
from libcore_hng.core.base_config import BaseConfig

class TestEncryptedConfigError:

    def test_invalid_token_displays_decryption_hint(self, tmp_path: Path, monkeypatch, capsys):
        """
        暗号化ファイルの復号失敗時にコンソールにヒントが表示されるか確認
        """
        project_root = tmp_path
        config_dir = project_root / "configs"
        config_dir.mkdir()

        encrypted_config = config_dir / "invalid-config.enc"
        encrypted_config.write_bytes(b"invalid encrypted data")

        monkeypatch.setenv("PROJECT_ROOT", str(project_root))
        monkeypatch.setenv("APP_SECRET_KEY", Fernet.generate_key().decode())

        BaseConfig.load_config(
            __file__,
            "invalid-config.enc",            
        )

        captured = capsys.readouterr()

        assert (
            "暗号化ファイルを復号できません。"
            "APP_SECRET_KEY が異なるか、暗号化ファイルが破損している可能性があります。"
            in captured.out
        )
        assert "invalid-config.enc" in captured.out