# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A small personal [pyinfra](https://pyinfra.com/) project for provisioning a local machine (`inventory.py` targets `localhost` only). `deploy.py` supports both Debian/Ubuntu (apt) and Arch Linux (pacman) hosts, picking the right package manager and package names at runtime. It's a learning/test project, not a multi-host production deploy — keep changes proportional to that.

## Setup

```bash
python3 -m venv .env
source .env/bin/activate
pip install -r requirements-dev.txt   # requirements.txt + pytest
```

Or via the Makefile: `make venv` (any other target depends on it and will run it automatically).

## Running

```bash
make dry-deploy   # preview deploy.py (no changes applied)
make deploy       # apply deploy.py
make dry-esp32    # preview esp32_arduino_setup.py
make esp32        # apply esp32_arduino_setup.py
```

The Makefile targets default to `HOST=@local`; override for a remote/inventory target, e.g. `make deploy HOST=inventory.py`. Equivalent raw commands: `pyinfra @local deploy.py [--dry]`.

Note: `"localhost"` as a bare hostname (as used in `inventory.py`) is resolved via pyinfra's **SSH connector** (it will try to SSH to `127.0.0.1:22`), not the local connector — an sshd must be running and reachable for the deploy to connect. `@local` bypasses SSH entirely and runs directly on the current machine, which is what the Makefile and `esp32_arduino_setup.py`'s own usage docstring use.

Makefile recipes pipe stderr through a filter that strips known-harmless `gevent`/`atfork` traceback noise (gevent doesn't yet support Python 3.14's threading internals) without hiding real errors — see the `NOISE_PATTERN` var in the Makefile.

## Testing

```bash
make test
# or directly:
pytest
```

Tests live in `tests/` and exercise the pure helper modules only (`distro_packages.py`, `group_utils.py`) — not the deploy scripts themselves, since those call `pyinfra.host.get_fact(...)` and operations at module scope, which requires a live pyinfra run context and can't be unit tested directly. `pytest.ini` sets `pythonpath = .` so tests can `import distro_packages` / `import group_utils` from the repo root.

## Architecture

- **`inventory.py`** — list of deploy targets (hosts/groups). Currently a single-host `localhost` inventory; would grow into host groups (e.g. `[("host1", {"ssh_user": "..."}), ...]`) if this expanded beyond one machine.
- **`deploy.py`** — general dev/terminal toolchain (build tooling, Python build deps for pyenv-style source builds, neovim, tmux, zsh, network/monitoring tools like `nmap`/`btop`/`screenfetch`). Reads the `LinuxName` fact and calls `distro_packages.resolve_packages()` to pick `apt.packages` (Debian/Ubuntu) or `pacman.packages` (Arch Linux) with the right package list per distro — Debian splits `-dev` packages out, Arch ships headers in the main package. An unrecognized distro raises `PyinfraError`.
- **`distro_packages.py`** — pure module (no pyinfra host access at import time) holding the two package lists and `resolve_packages()`; imported by both `deploy.py` and its tests.
- **`esp32_arduino_setup.py`** — ESP32/Arduino dev environment for Arch only (PlatformIO in a dedicated venv, Arduino IDE via `yay`, serial port group access, udev rule reload, an rclone Google Drive systemd `--user` mount unit). Run with `pyinfra @local esp32_arduino_setup.py` per its own docstring. Uses `group_utils.merge_secondary_groups()` when adding the user to the `uucp` group — pyinfra's `server.user(groups=...)` does a full replace (`usermod -G`), not an append, so existing group memberships (`wheel`, `docker`, etc.) must be merged in explicitly or they get wiped.
- **`group_utils.py`** — pure module holding `merge_secondary_groups()`; imported by `esp32_arduino_setup.py` and its tests.
- **`Makefile`** — wraps venv setup, tests, and both deploy scripts; see `make help`.

Both `deploy.py` and `esp32_arduino_setup.py` are executed by pyinfra via `exec()` with the current working directory on `sys.path` (not `import`), which is why `distro_packages`/`group_utils` can be imported as plain sibling modules as long as pyinfra is invoked from the repo root (the Makefile and documented commands both do this).
