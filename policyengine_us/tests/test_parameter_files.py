from datetime import date
from pathlib import Path

import yaml


PARAMETERS_DIR = Path(__file__).resolve().parents[1] / "parameters"
SOI_LONG_TERM_CAPITAL_GAINS_PATH = (
    PARAMETERS_DIR / "calibration/gov/irs/soi/long_term_capital_gains.yaml"
)
SOI_AGI_DIR = PARAMETERS_DIR / "calibration/gov/irs/soi/agi"
# IRS SOI Publication 1304 Table 1.1, "$1 under $5,000" and "$10,000,000 or
# more" rows: column 3 (AGI less deficit, published in thousands, stored here in
# dollars) for tax year 2020 and column 1 (number of returns) for tax year 2021.
SOI_AGI_BAND_TABLES = {
    "total_agi.yaml": (
        date(2020, 1, 1),
        "https://www.irs.gov/pub/irs-soi/20in11si.xls",
        24_087_842_000,
        824_093_126_000,
    ),
    "number_of_returns.yaml": (
        date(2021, 1, 1),
        "https://www.irs.gov/pub/irs-soi/21in11si.xls",
        8_487_025,
        45_404,
    ),
}
MI_INCOME_TAX_RATE_PATH = PARAMETERS_DIR / "gov/states/mi/tax/income/rate.yaml"
SOI_LONG_TERM_CAPITAL_GAINS_ANCHORS = {
    date(2015, 1, 1): 733_313_255_000,
    date(2020, 1, 1): 1_063_500_316_000,
    date(2023, 1, 1): 971_279_947_000,
}
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


def test_soi_long_term_capital_gains_uses_latest_publication_1304_anchor():
    parameter = yaml.safe_load(SOI_LONG_TERM_CAPITAL_GAINS_PATH.read_text())
    values = parameter["values"]

    for period, value in SOI_LONG_TERM_CAPITAL_GAINS_ANCHORS.items():
        assert values[period] == value

    assert max(values) >= date(2023, 1, 1)
    assert parameter["metadata"]["reference"][0]["href"].endswith(
        "publication-1304-basic-tables-part-1"
    )


def test_soi_agi_bands_are_keyed_to_their_table_1_1_tax_year():
    for filename, (period, href, lowest, highest) in SOI_AGI_BAND_TABLES.items():
        parameter = yaml.safe_load((SOI_AGI_DIR / filename).read_text())
        amounts = [bracket["amount"]["values"] for bracket in parameter["brackets"]]

        assert len(amounts) == 18, filename
        for index, values in enumerate(amounts):
            assert period in values, f"{filename} bracket {index} lacks {period}"
        assert amounts[0][period] == lowest, filename
        assert amounts[-1][period] == highest, filename
        reference = parameter["metadata"]["reference"][0]
        assert reference["href"] == href, filename
        assert f"tax year {period.year}" in reference["title"], filename


def test_mi_2026_income_tax_rate_uses_official_annual_determination():
    parameter = yaml.safe_load(MI_INCOME_TAX_RATE_PATH.read_text())

    assert parameter["values"][date(2026, 1, 1)] == 0.0425
    assert parameter["metadata"]["reference"][-1]["href"].endswith(
        "425-income-tax-rate-for-individuals-and-fiduciaries-in-2026-tax-year"
    )
