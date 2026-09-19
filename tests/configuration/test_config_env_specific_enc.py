import json
from pathlib import Path
from cryptography.fernet import Fernet
from libcore_hng.core.base_config import BaseConfig

def _write_encrypted_config(path: Path, payload: dict, key: str) -> None:
    encrypted = Fernet(key.encode()).encrypt(
        json.dumps(payload, ensure_ascii=False).encode("utf-8")        
    )
    path.write_bytes(encrypted)

def test_load_config_prefers_matching_env_specific_encrypted_file(monkeypatch, tmp_path: Path):
    project_root = tmp_path
    config_dir = project_root / "configs"
    config_dir.mkdir()

    key = Fernet.generate_key().decode()
    monkeypatch.setenv("PROJECT_ROOT", str(project_root))
    monkeypatch.setenv("APP_ENV", "prod")
    monkeypatch.setenv("APP_SECRET_KEY", key)

    _write_encrypted_config(
        config_dir / "app_config.dev.json.enc",
        {"gcp": {"project_id": "dev-project", "secret_name": "dev-secret"}},
        key,
    )
    _write_encrypted_config(
        config_dir / "app_config.prod.json.enc",
        {"gcp": {"project_id": "prod-project", "secret_name": "prod-secret"}},
        key,
    )

    cfg = BaseConfig.load_config(__file__)

    assert cfg.gcp.project_id == "prod-project"
    assert cfg.gcp.secret_name == "prod-secret"

def test_load_config_uses_general_encrypted_file_when_env_specific_file_missing(monkeypatch, tmp_path: Path):
    project_root = tmp_path
    config_dir = project_root / "configs"
    config_dir.mkdir()

    key = Fernet.generate_key().decode()
    monkeypatch.setenv("PROJECT_ROOT", str(project_root))
    monkeypatch.setenv("APP_ENV", "prod")
    monkeypatch.setenv("APP_SECRET_KEY", key)

    _write_encrypted_config(
        config_dir / "app_config.json.enc",
        {"gcp": {"project_id": "common-project", "secret_name": "common-secret"}},
        key,
    )

    cfg = BaseConfig.load_config(__file__)

    assert cfg.gcp.project_id == "common-project"
    assert cfg.gcp.secret_name == "common-secret"

def test_load_config_skips_non_matching_env_encrypted_file_when_matching_env_specific_file_exists(monkeypatch, tmp_path: Path):
    project_root = tmp_path
    config_dir = project_root / "configs"
    config_dir.mkdir()

    key = Fernet.generate_key().decode()
    monkeypatch.setenv("PROJECT_ROOT", str(project_root))
    monkeypatch.setenv("APP_ENV", "prod")
    monkeypatch.setenv("APP_SECRET_KEY", key)

    _write_encrypted_config(
        config_dir / "app_config.dev.json.enc",
        {"gcp": {"project_id": "dev-project", "secret_name": "dev-secret"}},
        key,
    )
    _write_encrypted_config(
        config_dir / "app_config.json.enc",
        {"gcp": {"project_id": "common-project", "secret_name": "common-secret"}},
        key,
    )

    cfg = BaseConfig.load_config(__file__)

    assert cfg.gcp.project_id == "common-project"
    