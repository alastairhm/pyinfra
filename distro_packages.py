"""Distro -> package manager/package list resolution for deploy.py.

Kept in its own plain-importable module (no pyinfra host/fact access at
import time) so the branching logic can be unit tested without a live
pyinfra run.
"""

from pyinfra.api.exceptions import PyinfraError

# Debian/Ubuntu package names (split -dev packages, python3-* naming)
APT_PACKAGES = [
        "btop",
        "build-essential",
        "chrony",
        "curl",
        "git",
        "jq",
        "libbz2-dev",
        "libffi-dev",
        "liblzma-dev",
        "libncurses5-dev",
        "libncursesw5-dev",
        "libreadline-dev",
        "libsqlite3-dev",
        "libssl-dev",
        "llvm",
        "neovim",
        "nmap",
        "python3",
        "python3-dev",
        "python3-pip",
        "screenfetch",
        "tk-dev",
        "tmux",
        "wget",
        "xz-utils",
        "zlib1g-dev",
        "zsh"
]

# Arch package names (no split -dev packages; headers ship in the main package)
PACMAN_PACKAGES = [
        "base-devel",
        "btop",
        "bzip2",
        "chrony",
        "curl",
        "git",
        "jq",
        "libffi",
        "llvm",
        "ncurses",
        "neovim",
        "nmap",
        "openssl",
        "python",
        "python-pip",
        "readline",
        "screenfetch",
        "sqlite",
        "tk",
        "tmux",
        "wget",
        "xz",
        "zlib",
        "zsh"
]

APT_DISTROS = ("Debian", "Ubuntu")
PACMAN_DISTROS = ("Arch Linux",)


def resolve_packages(distro):
    """Return (manager, packages) for a pyinfra `LinuxName` fact value.

    `manager` is "apt" or "pacman". Raises PyinfraError for any distro
    name not in APT_DISTROS/PACMAN_DISTROS.
    """
    if distro in APT_DISTROS:
        return "apt", APT_PACKAGES
    if distro in PACMAN_DISTROS:
        return "pacman", PACMAN_PACKAGES
    raise PyinfraError(
        "Unsupported distro {0!r}: deploy.py only supports Debian, Ubuntu, and Arch Linux".format(
            distro
        )
    )
