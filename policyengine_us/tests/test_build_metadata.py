from unittest.mock import patch

import pytest

from policyengine_us.build_metadata import (
    get_data_build_fingerprint,
    get_data_build_metadata,
    get_runtime_metadata,
)


def test_data_build_fingerprint_is_stable_within_process():
    get_data_build_fingerprint.cache_clear()

    first = get_data_build_fingerprint()
    second = get_data_build_fingerprint()

    assert first.startswith("sha256:")
    assert first == second


def test_get_runtime_metadata_includes_version_git_sha_fingerprint_and_core():
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
        patch(
            "policyengine_us.build_metadata.get_core_runtime_metadata",
            return_value={
                "name": "policyengine-core",
                "version": "3.26.0",
                "git_sha": "coredeadbeef",
            },
        ),
    ):
        metadata = get_runtime_metadata()

    assert metadata == {
        "name": "policyengine-us",
        "version": "1.602.0",
        "git_sha": "deadbeef",
        "data_build_fingerprint": "sha256:fingerprint",
        "core": {
            "name": "policyengine-core",
            "version": "3.26.0",
            "git_sha": "coredeadbeef",
        },
    }


def test_get_data_build_metadata_uses_runtime_metadata():
    with patch(
        "policyengine_us.build_metadata.get_runtime_metadata",
        return_value={"name": "policyengine-us"},
    ):
        assert get_data_build_metadata() == {"name": "policyengine-us"}


def test_runtime_metadata_uses_bundle_contract_when_available():
    policyengine_bundles = pytest.importorskip("policyengine_bundles")

    policyengine_bundles.load_component_metadata(get_runtime_metadata())
