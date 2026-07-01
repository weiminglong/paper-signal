from __future__ import annotations

import pytest

from paper_signal.cli import main
from paper_signal.onboarding import init_project


def test_doctor_missing_config_exits_nonzero(tmp_path, monkeypatch):
    monkeypatch.delenv("OBSIDIAN_VAULT_PATH", raising=False)
    with pytest.raises(SystemExit) as exc:
        main(["doctor", "--config", str(tmp_path / "nope.yaml"), "--vault", str(tmp_path), "--offline"])
    assert exc.value.code == 1


def test_run_missing_config_is_friendly(tmp_path, monkeypatch, capsys):
    monkeypatch.delenv("OBSIDIAN_VAULT_PATH", raising=False)
    with pytest.raises(SystemExit) as exc:
        main(["run", "--config", str(tmp_path / "nope.yaml"), "--vault", str(tmp_path)])
    assert exc.value.code == 1
    err = capsys.readouterr().err
    # Friendly message, not a raw traceback, and it points at `init`.
    assert "Config error" in err
    assert "paper-signal init" in err


def test_doctor_distinguishes_warnings_from_all_good(tmp_path, monkeypatch, capsys):
    # A not-yet-created vault is a warning, not a failure — the summary must say so,
    # not print a bare "All good." next to a ⚠ line.
    monkeypatch.delenv("OBSIDIAN_VAULT_PATH", raising=False)
    config_path = tmp_path / "interests.yaml"
    init_project(config_path=config_path, vault=None)
    # Does not raise (all_ok is True), but warns.
    main(["doctor", "--config", str(config_path), "--vault", str(tmp_path / "not-created"), "--offline"])
    out = capsys.readouterr().out
    assert "All good (with warnings)." in out
    assert "does not exist yet" in out


def test_init_numbers_steps_contiguously(tmp_path, monkeypatch, capsys):
    monkeypatch.delenv("OBSIDIAN_VAULT_PATH", raising=False)
    main(["init", "--config", str(tmp_path / "interests.yaml")])
    out = capsys.readouterr().out
    # No vault provided -> four steps, numbered 1..4 with no gap.
    assert "  1. Edit your research domains" in out
    assert "  2. Set your vault" in out
    assert "  3. Verify setup" in out
    assert "  4. First run" in out


def test_init_skips_vault_step_but_stays_contiguous(tmp_path, monkeypatch, capsys):
    monkeypatch.delenv("OBSIDIAN_VAULT_PATH", raising=False)
    main(["init", "--config", str(tmp_path / "interests.yaml"), "--vault", str(tmp_path / "vault")])
    out = capsys.readouterr().out
    # Vault provided -> the "Set your vault" step is omitted, numbering stays 1..3.
    assert "Set your vault" not in out
    assert "  2. Verify setup" in out
    assert "  3. First run" in out
    assert "  4. " not in out
