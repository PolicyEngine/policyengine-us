import pytest
import yaml

from policyengine_core.parameters import Parameter, ParameterNode
from policyengine_core.parameters.operations import propagate_parameter_metadata
from policyengine_us.model_api import REPO
from policyengine_us.system import system


PARAMETERS_ROOT = REPO / "parameters"


class _NoTimestampSafeLoader(yaml.SafeLoader):
    """`yaml.SafeLoader` with the implicit timestamp resolver disabled.

    Several parameter files use `0000-01-01` as a "since the beginning of
    time" sentinel key (e.g. a bracket that applies from year zero until an
    explicit later value takes over). Python's `datetime.date` cannot
    represent year 0, so PyYAML's default date resolver raises on these
    files. Since we only need dict/list structure here (not date parsing),
    disabling the resolver lets those keys load as plain strings instead of
    crashing.
    """


_NoTimestampSafeLoader.yaml_implicit_resolvers = {
    key: [
        (tag, regexp)
        for tag, regexp in resolvers
        if tag != "tag:yaml.org,2002:timestamp"
    ]
    for key, resolvers in yaml.SafeLoader.yaml_implicit_resolvers.items()
}


def _find_sibling_values_uprating_nodes(
    node, path: str, violations: list[str], file_label: str
) -> None:
    """Recursively flag any dict node with both `values` and `uprating` as
    direct sibling keys -- the placement the parameter loader silently
    ignores (see #8905). The working placement nests `uprating` one level
    deeper, under that node's own `metadata` key."""
    if isinstance(node, dict):
        if "values" in node and "uprating" in node:
            violations.append(f"{file_label} @ {path or '/'}")
        for key, value in node.items():
            _find_sibling_values_uprating_nodes(
                value, f"{path}/{key}", violations, file_label
            )
    elif isinstance(node, list):
        for index, item in enumerate(node):
            _find_sibling_values_uprating_nodes(
                item, f"{path}[{index}]", violations, file_label
            )


def test_no_uprating_block_is_a_sibling_of_values():
    assert PARAMETERS_ROOT.exists(), (
        f"Expected parameters root to exist: {PARAMETERS_ROOT}"
    )

    violations: list[str] = []
    parse_errors: list[str] = []

    for file_name in sorted(PARAMETERS_ROOT.glob("**/*.yaml")):
        file_label = file_name.relative_to(PARAMETERS_ROOT).as_posix()
        with open(file_name) as handle:
            try:
                data = yaml.load(handle, Loader=_NoTimestampSafeLoader)
            except yaml.YAMLError as error:
                parse_errors.append(f"{file_label}: {error}")
                continue
        _find_sibling_values_uprating_nodes(data, "", violations, file_label)

    assert not parse_errors, (
        "Failed to parse parameter YAML while scanning for uprating "
        "placement. Fix the underlying YAML before this check can run:\n"
        + "\n".join(parse_errors)
    )

    assert not violations, (
        "Found `uprating:` written as a sibling of `values:` instead of "
        "nested under that node's `metadata:` key. The parameter loader "
        "silently ignores `uprating:` in this position, freezing the "
        "parameter at its last explicit value instead of projecting it "
        "forward (see #8905). Move each offending block from:\n"
        "    values:\n"
        "      ...\n"
        "    uprating:\n"
        "      parameter: ...\n"
        "to:\n"
        "    values:\n"
        "      ...\n"
        "    metadata:\n"
        "      uprating:\n"
        "        parameter: ...\n"
        "Offending nodes:\n" + "\n".join(violations)
    )


def _find_unapplied_breakdown_uprating(root):
    """Find parent uprating that reaches no metadata on some scalar leaves."""
    violations = {}
    for node in root.get_descendants():
        if not isinstance(node, ParameterNode):
            continue
        if not node.metadata.get("breakdown"):
            continue
        if node.metadata.get("uprating") is None:
            continue
        missing = [
            leaf.name
            for leaf in node.get_descendants()
            if isinstance(leaf, Parameter) and leaf.metadata.get("uprating") is None
        ]
        if missing:
            violations[node.name] = missing
    return violations


def test_parent_uprating_reaches_breakdown_leaves():
    violations = _find_unapplied_breakdown_uprating(system.parameters)
    assert not violations, (
        "The built parameter system omits uprating from leaves below parents "
        "that declare both breakdown and uprating metadata. Add uprating to "
        "each leaf, enable metadata propagation, or remove unsupported parent "
        "uprating:\n"
        + "\n".join(
            f"{parent}: {', '.join(leaves)}"
            for parent, leaves in sorted(violations.items())
        )
    )


@pytest.mark.parametrize(
    "propagation, leaf_uprating, missing",
    [
        (None, (), ("SINGLE", "JOINT")),
        (True, (), ()),
        (False, (), ("SINGLE", "JOINT")),
        (False, ("SINGLE", "JOINT"), ()),
        (False, ("SINGLE",), ("JOINT",)),
    ],
)
def test_detect_unapplied_parent_uprating(propagation, leaf_uprating, missing):
    metadata = {
        "breakdown": ["filing_status"],
        "uprating": "price_index",
    }
    if propagation is not None:
        metadata["propagate_metadata_to_children"] = propagation
    threshold = {"metadata": metadata}
    for status in ("SINGLE", "JOINT"):
        threshold[status] = {"values": {"2024-01-01": 100}}
        if status in leaf_uprating:
            threshold[status]["metadata"] = {"uprating": "price_index"}
    root = ParameterNode("", data={"threshold": threshold})
    propagate_parameter_metadata(root)

    expected = (
        {"threshold": [f"threshold.{status}" for status in missing]} if missing else {}
    )
    assert _find_unapplied_breakdown_uprating(root) == expected
