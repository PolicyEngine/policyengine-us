from datetime import date
from pathlib import Path

import yaml


PARAMETERS_DIR = Path(__file__).resolve().parents[1] / "parameters"
PARAMETER_SCHEMA_KEYS = {
    "brackets",
    "description",
    "documentation",
    "label",
    "metadata",
    "reference",
    "unit",
    "values",
}


class NoDatesSafeLoader(yaml.SafeLoader):
    pass


NoDatesSafeLoader.yaml_implicit_resolvers = {
    key: [
        (tag, regexp)
        for tag, regexp in resolvers
        if tag != "tag:yaml.org,2002:timestamp"
    ]
    for key, resolvers in yaml.SafeLoader.yaml_implicit_resolvers.items()
}


def _enum_breakdown_parameter_errors(path, data):
    if not isinstance(data, dict):
        return []

    metadata = data.get("metadata") or {}
    if "breakdown" not in metadata:
        return []

    breakdown = metadata["breakdown"]
    parameter_keys = [key for key in data if key not in PARAMETER_SCHEMA_KEYS]
    relative_path = path.relative_to(PARAMETERS_DIR.parent)

    if len(parameter_keys) == 0 and ("values" in data or "brackets" in data):
        return [
            f"{relative_path} has metadata.breakdown={breakdown!r} "
            "but no top-level enum members. Remove metadata.breakdown "
            "from scalar parameters."
        ]

    if len(parameter_keys) == 1:
        return [
            f"{relative_path} has metadata.breakdown={breakdown!r} "
            f"but only one top-level member {parameter_keys[0]!r}. "
            "Use a scalar parameter under a member-specific path instead."
        ]

    return []


def test_parameter_yaml_files_are_syntax_parseable():
    errors = []

    for path in sorted(PARAMETERS_DIR.rglob("*.yaml")):
        try:
            yaml.compose(path.read_text())
        except yaml.YAMLError as exc:
            errors.append(f"{path.relative_to(PARAMETERS_DIR.parent)}: {exc}")

    assert errors == []


def test_calworks_yaml_fixes_preserve_effective_dates():
    max_au_size = yaml.safe_load(
        (
            PARAMETERS_DIR
            / "gov/states/ca/cdss/tanf/cash/monthly_payment/max_au_size.yaml"
        ).read_text()
    )
    region1_counties = yaml.safe_load(
        (
            PARAMETERS_DIR / "gov/states/ca/cdss/tanf/cash/region1_counties.yaml"
        ).read_text()
    )

    assert list(max_au_size["values"].keys()) == [date(2023, 10, 1)]
    assert list(region1_counties["values"].keys()) == [date(2023, 7, 1)]


def test_enum_breakdown_guard_rejects_scalar_parameters_with_breakdown():
    errors = _enum_breakdown_parameter_errors(
        PARAMETERS_DIR / "gov/hhs/tanf/non_cash/income_limit/ny/earned_income.yaml",
        {
            "description": "New York SNAP BBCE gross income limit.",
            "values": {"2026-01-01": 1.5},
            "metadata": {"breakdown": ["state_code"]},
        },
    )

    assert len(errors) == 1
    assert "metadata.breakdown" in errors[0]


def test_enum_breakdown_guard_ignores_reference_when_counting_members():
    errors = _enum_breakdown_parameter_errors(
        PARAMETERS_DIR / "gov/hhs/tanf/non_cash/income_limit/earned.yaml",
        {
            "description": "SNAP BBCE gross income limit.",
            "NY": {"2026-01-01": 1.5},
            "reference": [{"title": "Example source"}],
            "metadata": {"breakdown": ["state_code"]},
        },
    )

    assert len(errors) == 1
    assert "only one top-level member 'NY'" in errors[0]


def test_enum_breakdown_parameters_do_not_have_single_member_tables():
    errors = []

    for path in sorted(PARAMETERS_DIR.rglob("*.yaml")):
        data = yaml.load(path.read_text(), Loader=NoDatesSafeLoader)
        errors.extend(_enum_breakdown_parameter_errors(path, data))

    assert errors == []
