"""
Unit tests for the CLI module.
"""

from photon_mosaic.cli import build_snakemake_command


def test_build_snakemake_command_basic(cli_args, snake_test_env):
    """Test that build_snakemake_command returns a valid command."""
    configfile = snake_test_env["configfile"]

    cmd = build_snakemake_command(cli_args, configfile)

    assert "snakemake" in cmd
    assert "--configfile" in cmd
    assert str(configfile) in cmd


def test_build_snakemake_command_dry_run(cli_args, snake_test_env):
    """Test that --dry-run is added when set in args."""
    import argparse

    configfile = snake_test_env["configfile"]

    dry_run_args = argparse.Namespace(
        config=str(configfile),
        jobs="1",
        dry_run=True,
        forcerun=None,
        rerun_incomplete=False,
        latency_wait=10,
        verbose=False,
    )

    cmd = build_snakemake_command(dry_run_args, configfile)

    assert "--dry-run" in cmd
