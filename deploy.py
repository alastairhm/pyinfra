from pyinfra import host
from pyinfra.api.exceptions import PyinfraError
from pyinfra.facts.server import LinuxName
from pyinfra.operations import apt, pacman

# Debian/Ubuntu package names (split -dev packages, python3-* naming)
apt_packages = [
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
pacman_packages = [
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

distro = host.get_fact(LinuxName)

if distro in ("Debian", "Ubuntu"):
    apt.packages(
        name="Ensure packages are installed",
        packages=apt_packages,
        update=True,
        _sudo=True
    )
elif distro == "Arch Linux":
    pacman.packages(
        name="Ensure packages are installed",
        packages=pacman_packages,
        update=True,
        _sudo=True
    )
else:
    raise PyinfraError(
        "Unsupported distro {0!r}: deploy.py only supports Debian, Ubuntu, and Arch Linux".format(
            distro
        )
    )
