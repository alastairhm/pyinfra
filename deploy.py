from pyinfra import host
from pyinfra.facts.server import LinuxName
from pyinfra.operations import apt, pacman

from distro_packages import resolve_packages

distro = host.get_fact(LinuxName)
manager, packages = resolve_packages(distro)

if manager == "apt":
    apt.packages(
        name="Ensure packages are installed",
        packages=packages,
        update=True,
        _sudo=True
    )
else:
    pacman.packages(
        name="Ensure packages are installed",
        packages=packages,
        update=True,
        _sudo=True
    )
