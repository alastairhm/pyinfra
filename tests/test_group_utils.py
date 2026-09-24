from group_utils import merge_secondary_groups


def test_adds_new_group_to_existing():
    assert merge_secondary_groups(["wheel", "docker"], ["uucp"]) == ["docker", "uucp", "wheel"]


def test_preserves_all_existing_groups():
    existing = ["wheel", "docker", "video", "audio"]
    result = merge_secondary_groups(existing, ["uucp"])
    assert set(existing).issubset(set(result))


def test_is_idempotent_when_group_already_present():
    assert merge_secondary_groups(["wheel", "uucp"], ["uucp"]) == ["uucp", "wheel"]


def test_handles_no_existing_groups():
    assert merge_secondary_groups([], ["uucp"]) == ["uucp"]


def test_result_has_no_duplicates():
    result = merge_secondary_groups(["uucp", "wheel"], ["uucp", "docker"])
    assert result == sorted(set(result))
    assert result == ["docker", "uucp", "wheel"]
