"""Small pure helper factored out of esp32_arduino_setup.py so it's
unit-testable without a live pyinfra host context.
"""


def merge_secondary_groups(existing_groups, additional_groups):
    """Return the sorted union of a user's existing secondary groups and
    the groups a deploy wants to add.

    pyinfra's server.user(groups=...) does a full `usermod -G` replace, not
    an append, so callers must merge in the existing groups themselves to
    avoid dropping a user from wheel/docker/etc.
    """
    return sorted(set(existing_groups) | set(additional_groups))
