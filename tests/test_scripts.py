from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "scripts"
_SCRIPT_NAMES = ["run-daily.sh", "install_cron.sh", "install_launchd.sh"]

pytestmark = pytest.mark.skipif(shutil.which("bash") is None, reason="bash not available")


@pytest.mark.parametrize("name", _SCRIPT_NAMES)
def test_script_passes_bash_syntax(name):
    subprocess.run(["bash", "-n", str(SCRIPTS / name)], check=True)


def test_run_daily_passes_spaced_vault_as_single_arg(tmp_path):
    """run-daily.sh must forward a vault path containing spaces as one argv token."""
    argv_out = tmp_path / "argv.txt"
    shim = tmp_path / "fake-paper-signal"
    shim.write_text('#!/usr/bin/env bash\nprintf "%s\\n" "$@" > "$SHIM_OUT"\n', encoding="utf-8")
    shim.chmod(0o755)

    vault = "/tmp/My Obsidian Vault"  # contains a space
    env = dict(os.environ)
    env.update(
        {
            "PAPER_SIGNAL_BIN": str(shim),
            "OBSIDIAN_VAULT_PATH": vault,
            "PAPER_SIGNAL_CONFIG": str(tmp_path / "interests.yaml"),
            "SHIM_OUT": str(argv_out),
        }
    )
    subprocess.run(["bash", str(SCRIPTS / "run-daily.sh")], check=True, env=env)

    args = argv_out.read_text(encoding="utf-8").splitlines()
    assert args[0] == "run"
    assert "--vault" in args
    assert args[args.index("--vault") + 1] == vault  # space preserved as a single arg


def test_install_scripts_reject_bad_hour(tmp_path):
    for name in ["install_cron.sh", "install_launchd.sh"]:
        result = subprocess.run(
            ["bash", str(SCRIPTS / name), "9am"],
            capture_output=True,
            text=True,
        )
        assert result.returncode != 0
        assert "HOUR must be an integer" in result.stderr
