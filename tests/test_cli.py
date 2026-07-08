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


def test_history_resolves_vault_from_config(tmp_path, monkeypatch, capsys):
    """commit/unsee/history must fall back to the config's vault_path — the skills
    promise one resolution order for every command."""
    monkeypatch.delenv("OBSIDIAN_VAULT_PATH", raising=False)
    vault = tmp_path / "vault"
    config_path = tmp_path / "interests.yaml"
    config_path.write_text(
        f'vault_path: "{vault}"\nresearch_domains:\n  X:\n    keywords: [x]\n',
        encoding="utf-8",
    )
    main(["history", "--config", str(config_path)])  # no --vault, no env
    out = capsys.readouterr().out
    assert "No papers recorded" in out


def test_report_mode_parsed_and_in_fetch_payload(tmp_path):
    from paper_signal.config import load_config
    from paper_signal.pipeline import FetchResult, fetch_payload
    from datetime import date
    from pathlib import Path

    config_path = tmp_path / "interests.yaml"
    config_path.write_text(
        "daily:\n  report_mode: quick\nresearch_domains:\n  X:\n    keywords: [x]\n",
        encoding="utf-8",
    )
    config = load_config(config_path)
    assert config.daily.report_mode == "quick"
    payload = fetch_payload(
        FetchResult(
            config=config, vault_path=Path("/v"), run_date=date(2026, 7, 3),
            fetched_count=0, candidate_count=0, selected=[],
        )
    )
    assert payload["report_mode"] == "quick"

    # Unknown values fall back to "full".
    config_path.write_text(
        "daily:\n  report_mode: turbo\nresearch_domains:\n  X:\n    keywords: [x]\n",
        encoding="utf-8",
    )
    assert load_config(config_path).daily.report_mode == "full"


def test_corrupt_state_yields_friendly_cli_error(tmp_path, monkeypatch, capsys):
    monkeypatch.delenv("OBSIDIAN_VAULT_PATH", raising=False)
    vault = tmp_path / "vault"
    state_path = vault / "99_System" / "PaperSignal" / "state.json"
    state_path.parent.mkdir(parents=True)
    state_path.write_text("not json{", encoding="utf-8")

    with pytest.raises(SystemExit) as exc:
        main(["history", "--vault", str(vault)])
    assert exc.value.code == 1
    err = capsys.readouterr().err
    assert "State error" in err
    assert "Traceback" not in err
    assert "state.json.bak" in err


def test_history_output_includes_arxiv_links(tmp_path, monkeypatch, capsys):
    monkeypatch.delenv("OBSIDIAN_VAULT_PATH", raising=False)
    from paper_signal.pipeline import commit_seen
    from datetime import date

    vault = tmp_path / "vault"
    commit_seen(
        vault, ["2607.00001v1"],
        entries=[{"paper_id": "2607.00001v1", "title": "T", "score": 4.0, "date": date.today().isoformat()}],
    )
    main(["history", "--vault", str(vault)])
    out = capsys.readouterr().out
    assert "https://arxiv.org/abs/2607.00001v1" in out
    assert "score = keyword-match relevance" in out


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
