import pytest
from pyinfra.api.exceptions import PyinfraError

from distro_packages import APT_PACKAGES, PACMAN_PACKAGES, resolve_packages


@pytest.mark.parametrize("distro", ["Debian", "Ubuntu"])
def test_resolve_packages_picks_apt(distro):
    manager, packages = resolve_packages(distro)
    assert manager == "apt"
    assert packages is APT_PACKAGES


def test_resolve_packages_picks_pacman():
    manager, packages = resolve_packages("Arch Linux")
    assert manager == "pacman"
    assert packages is PACMAN_PACKAGES


@pytest.mark.parametrize("distro", ["Fedora", "CentOS", "", None])
def test_resolve_packages_rejects_unsupported_distro(distro):
    with pytest.raises(PyinfraError):
        resolve_packages(distro)


def test_unsupported_distro_error_message_names_the_distro():
    with pytest.raises(PyinfraError, match="Fedora"):
        resolve_packages("Fedora")


@pytest.mark.parametrize("packages", [APT_PACKAGES, PACMAN_PACKAGES], ids=["apt", "pacman"])
def test_package_lists_have_no_duplicates(packages):
    assert len(packages) == len(set(packages))


@pytest.mark.parametrize("pkg", ["git", "zsh", "tmux", "neovim", "curl", "chrony", "nmap"])
def test_core_toolchain_present_in_both_lists(pkg):
    assert pkg in APT_PACKAGES
    assert pkg in PACMAN_PACKAGES
