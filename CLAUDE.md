# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A small personal [pyinfra](https://pyinfra.com/) project for provisioning a local Debian/Ubuntu-based machine (`inventory.py` targets `localhost` only). It's a learning/test project, not a multi-host production deploy — keep changes proportional to that.

## Setup

```bash
python3 -m venv .env
source .env/bin/activate
pip install -r requirements.txt
```

## Running

```bash
pyinfra inventory.py deploy.py
```

- `inventory.py` defines the target hosts (currently just `["localhost"]`).
- `deploy.py` defines the operations to run against those hosts.

Since the only target is `localhost` and the `apt.packages` operation uses `_sudo=True`, running the deploy will prompt for the local sudo password (pyinfra connects to localhost as a "local" connector, not SSH).

Add `-v` for verbose output, or `--dry` to preview changes without applying them (standard pyinfra CLI flags — see `pyinfra --help`).

## Architecture

Structure follows pyinfra's standard two-file convention:

- **`inventory.py`** — list of deploy targets (hosts/groups). Currently a single-host `localhost` inventory; would grow into host groups (e.g. `[("host1", {"ssh_user": "..."}), ...]`) if this expanded beyond one machine.
- **`deploy.py`** — the actual operations, built from `pyinfra.operations` modules (currently just `apt.packages` to install a fixed list of packages). Additional deploy steps would typically go here as more `pyinfra.operations` calls (e.g. `files`, `server`, `systemd`), or be split into separate op files and imported if `deploy.py` grows large.

The package list in `deploy.py` is a general-purpose dev/terminal toolchain (build tooling, Python build deps for pyenv-style source builds, neovim, tmux, zsh, network/monitoring tools like `nmap`/`btop`/`screenfetch`).
