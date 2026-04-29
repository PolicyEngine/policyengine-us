from unittest.mock import patch

from policyengine_us.build_metadata import (
    get_data_build_fingerprint,
    get_data_build_metadata,
)


def test_data_build_fingerprint_is_stable_within_process():
    get_data_build_fingerprint.cache_clear()

    first = get_data_build_fingerprint()
    second = get_data_build_fingerprint()

    assert first.startswith("sha256:")
    assert first == second


def test_get_data_build_metadata_includes_version_git_sha_and_fingerprint():
    get_data_build_fingerprint.cache_clear()

    with (
        patch(
            "policyengine_us.build_metadata._get_package_version",
            return_value="1.602.0",
        ),
        patch(
            "policyengine_us.build_metadata._get_git_sha",
            return_value="deadbeef",
        ),
        patch(
            "policyengine_us.build_metadata.get_data_build_fingerprint",
            return_value="sha256:fingerprint",
        ),
    ):
        metadata = get_data_build_metadata()

    assert metadata == {
        "name": "policyengine-us",
        "version": "1.602.0",
        "git_sha": "deadbeef",
        "data_build_fingerprint": "sha256:fingerprint",
    }
