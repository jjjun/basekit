import pytest

from basekit.vault import Vault


def test_vault_get_returns_named_section(tmp_path):
    vault_path = tmp_path / "vault.toml"
    vault_path.write_text(
        """
[google]
api_key = "abc"
enabled = true
""".strip(),
        encoding="utf-8",
    )

    vault = Vault(vault_toml_file_path=vault_path)

    assert vault.get("google") == {"api_key": "abc", "enabled": True}


def test_vault_get_without_name_returns_all_data(tmp_path):
    vault_path = tmp_path / "vault.toml"
    vault_path.write_text(
        """
[service]
token = "secret"
""".strip(),
        encoding="utf-8",
    )

    vault = Vault(vault_toml_file_path=str(vault_path))

    assert vault.get() == {"service": {"token": "secret"}}


def test_vault_requires_path():
    vault = Vault()

    with pytest.raises(ValueError, match="vault_toml_file_path is required"):
        vault.get()
