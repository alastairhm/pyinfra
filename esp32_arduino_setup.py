"""
pyinfra deploy: ESP32 / Arduino development setup for Arch Linux

Installs:
  - PlatformIO Core (pip, user-level) — primary workflow
  - Arduino IDE (AUR, via yay) — for quick sketches
  - Serial port access (uucp group)
  - udev rules refresh for common USB-serial chips (CP2102 / CH340)
  - rclone + a systemd --user unit that mounts Google Drive at ~/gdrive on login

Usage:
    pyinfra @local esp32_arduino_setup.py
    pyinfra <host> esp32_arduino_setup.py

Notes:
  - Assumes yay is already installed. pyinfra has no native AUR support, so
    the Arduino IDE package is installed via a plain shell command and will
    fail if yay isn't present.
  - Run as your normal user (not root) for the AUR/pip steps; pyinfra will
    prompt for sudo only where needed (group membership, pacman packages).
  - rclone's Google Drive OAuth flow is interactive (opens a browser to
    authorize), so it can't be scripted here. After this runs, do a one-time
    `rclone config` and name the remote "gdrive" — then the systemd --user
    unit below will mount it automatically on every login.
"""

from pyinfra import host
from pyinfra.operations import pacman, pip, server
from pyinfra.facts.server import User, Users

current_user = host.get_fact(User)
existing_groups = host.get_fact(Users).get(current_user, {}).get("groups", [])

# ---------------------------------------------------------------------------
# 1. Base packages via pacman
# ---------------------------------------------------------------------------
pacman.packages(
    name="Install base packages (python, pip, git, usb tools)",
    packages=[
        "python",
        "python-pip",
        "git",
        "usbutils",
        "picocom",  # handy for quick serial console checks
        "rclone",
        "fuse3",
    ],
    update=True,
    _sudo=True,
)

# ---------------------------------------------------------------------------
# 2. Serial port access
# ---------------------------------------------------------------------------
server.user(
    name="Add user to uucp group for serial port access",
    user=current_user,
    # `groups` is a full replace (usermod -G), not an append — keep the
    # user's existing secondary groups (wheel, docker, etc.) intact.
    groups=sorted(set(existing_groups) | {"uucp"}),
    _sudo=True,
)

# ---------------------------------------------------------------------------
# 3. PlatformIO Core (pip, into a dedicated venv — no root needed)
# ---------------------------------------------------------------------------
# Arch's python-pip ships PEP 668's EXTERNALLY-MANAGED marker, so a plain
# `pip install --user` is refused. Installing into our own venv (via the
# stdlib `venv` module, since `virtualenv` itself isn't installed) sidesteps
# that entirely.
PIO_VENV = "$HOME/.local/share/pio-venv"

pip.packages(
    name="Install PlatformIO Core",
    packages=["platformio"],
    virtualenv=PIO_VENV,
    virtualenv_kwargs={"venv": True},
)

# Pre-fetch the ESP32 platform + toolchain so the first build isn't a
# surprise multi-hundred-MB download
server.shell(
    name="Pre-install PlatformIO ESP32 platform",
    commands=[f"{PIO_VENV}/bin/pio pkg install --global --platform espressif32"],
)

# ---------------------------------------------------------------------------
# 4. Arduino IDE (AUR via yay)
# ---------------------------------------------------------------------------
server.shell(
    name="Install Arduino IDE via yay",
    commands=["yay -S --needed --noconfirm arduino-ide"],
)

# ---------------------------------------------------------------------------
# 5. Reload udev rules (covers CP2102 / CH340 USB-serial chips, which are
#    supported in-kernel on modern Arch but this ensures rules are fresh)
# ---------------------------------------------------------------------------
server.shell(
    name="Reload udev rules",
    commands=["udevadm control --reload-rules && udevadm trigger"],
    _sudo=True,
)

server.shell(
    name="Remind: relog required for uucp group membership to take effect",
    commands=["echo 'NOTE: log out/in (or reboot) for serial port group access to apply'"],
)

# ---------------------------------------------------------------------------
# 6. rclone Google Drive mount (auto-mounts at ~/gdrive on login)
# ---------------------------------------------------------------------------
server.shell(
    name="Create rclone mount point and systemd user unit dir",
    commands=[
        "mkdir -p $HOME/gdrive",
        "mkdir -p $HOME/.config/systemd/user",
    ],
)

RCLONE_UNIT = """[Unit]
Description=Mount Google Drive via rclone
AssertPathIsDirectory=%h/gdrive
After=network-online.target
Wants=network-online.target

[Service]
Type=notify
ExecStart=/usr/bin/rclone mount gdrive: %h/gdrive \\
    --vfs-cache-mode writes \\
    --dir-cache-time 1h \\
    --poll-interval 1m
ExecStop=/bin/fusermount3 -u %h/gdrive
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
"""

server.shell(
    name="Write rclone-gdrive systemd user unit",
    commands=[
        "cat > $HOME/.config/systemd/user/rclone-gdrive.service << 'EOF'\n"
        + RCLONE_UNIT
        + "EOF"
    ],
)

server.shell(
    name="Reload and enable rclone-gdrive user service (starts after rclone config is run)",
    commands=[
        "systemctl --user daemon-reload",
        "systemctl --user enable rclone-gdrive.service",
    ],
)
