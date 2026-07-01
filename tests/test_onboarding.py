from __future__ import annotations

from paper_signal.config import load_config
from paper_signal.onboarding import doctor, init_project


def _statuses(checks):
    return {check.name: check.status for check in checks}


def test_init_creates_config(tmp_path):
    config_path = tmp_path / "config" / "interests.yaml"
    result = init_project(config_path=config_path, vault=None)

    assert result.created_config is True
    assert config_path.exists()
    assert "research_domains" in config_path.read_text(encoding="utf-8")
    # Config parses and has at least one domain.
    assert len(load_config(config_path).research_domains) >= 1


def test_init_sets_vault_and_scaffolds(tmp_path):
    config_path = tmp_path / "interests.yaml"
    vault = tmp_path / "vault"
    result = init_project(config_path=config_path, vault=str(vault))

    assert result.scaffolded is True
    assert (vault / "10_Daily").is_dir()
    assert (vault / "99_System" / "PaperSignal").is_dir()
    # The vault path was baked into the written config.
    assert load_config(config_path).vault_path == str(vault)


def test_init_does_not_overwrite_without_force(tmp_path):
    config_path = tmp_path / "interests.yaml"
    config_path.write_text("language: en\nresearch_domains:\n  X:\n    keywords: [x]\n", encoding="utf-8")

    result = init_project(config_path=config_path, vault=None)
    assert result.created_config is False
    assert "language: en" in config_path.read_text(encoding="utf-8")

    forced = init_project(config_path=config_path, vault=None, force=True)
    assert forced.created_config is True
    assert "PaperSignal interests" in config_path.read_text(encoding="utf-8")


def test_doctor_fails_without_config(tmp_path):
    all_ok, checks = doctor(config_path=tmp_path / "missing.yaml", vault=str(tmp_path), offline=True)
    assert all_ok is False
    assert _statuses(checks)["config"] == "fail"


def test_doctor_ok_with_valid_setup(tmp_path):
    config_path = tmp_path / "interests.yaml"
    vault = tmp_path / "vault"
    init_project(config_path=config_path, vault=str(vault))

    all_ok, checks = doctor(config_path=config_path, vault=str(vault), offline=True)
    statuses = _statuses(checks)
    assert all_ok is True
    assert statuses["config"] == "ok"
    assert statuses["vault"] == "ok"


def test_init_force_new_reports_wrote(tmp_path):
    # --force on a path with no existing config should say "Wrote", not "Overwrote".
    config_path = tmp_path / "interests.yaml"
    result = init_project(config_path=config_path, vault=None, force=True)
    assert result.created_config is True
    assert any("Wrote config" in note for note in result.notes)
    assert not any("Overwrote" in note for note in result.notes)


def test_init_handles_special_char_vault_paths(tmp_path):
    # Real, creatable dirs whose names contain the exact chars that broke raw YAML
    # interpolation: a double-quote, and a backslash followed by U (a YAML \U escape).
    for name in ['My "Cool" Vault', r"C\Users Vault"]:
        vault = tmp_path / name
        config_path = tmp_path / "interests.yaml"
        init_project(config_path=config_path, vault=str(vault), force=True)
        # The written config must parse and preserve the exact vault path.
        assert load_config(config_path).vault_path == str(vault)


def test_doctor_state_check_ok_and_warn(tmp_path):
    config_path = tmp_path / "interests.yaml"
    vault = tmp_path / "vault"
    init_project(config_path=config_path, vault=str(vault))
    state_file = vault / "99_System" / "PaperSignal" / "state.json"

    state_file.write_text('{"seen_paper_ids": ["a", "b"]}', encoding="utf-8")
    ok, checks = doctor(config_path=config_path, vault=str(vault), offline=True)
    statuses = _statuses(checks)
    assert statuses["state"] == "ok"
    assert ok is True

    # A corrupt state file is a warning, not a hard failure (dedup can be reset).
    state_file.write_text("not json{", encoding="utf-8")
    ok2, checks2 = doctor(config_path=config_path, vault=str(vault), offline=True)
    assert _statuses(checks2)["state"] == "warn"
    assert ok2 is True


def test_doctor_warns_on_empty_keywords(tmp_path):
    config_path = tmp_path / "interests.yaml"
    config_path.write_text(
        "vault_path: \"\"\nresearch_domains:\n  Empty:\n    priority: 1\n    keywords: []\n",
        encoding="utf-8",
    )
    all_ok, checks = doctor(config_path=config_path, vault=str(tmp_path), offline=True)
    statuses = _statuses(checks)
    assert statuses.get("domains") == "warn"
    # No vault problems (tmp_path exists and is writable), so overall passes.
    assert all_ok is True
