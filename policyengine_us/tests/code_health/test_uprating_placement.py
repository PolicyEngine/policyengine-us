import yaml

from policyengine_us.model_api import REPO


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
