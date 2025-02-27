from pyinfra.operations import apt

packages = [
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

apt.packages(
    name="Ensure packages are installed",
    packages=packages,
    update=True,
    _sudo=True
)
