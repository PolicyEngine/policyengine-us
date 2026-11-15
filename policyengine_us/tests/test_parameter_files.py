import re
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
SOI_DIR = PARAMETERS_DIR / "calibration/gov/irs/soi"
SOI_TABLE_1_4_FILE = re.compile(
    r"https://www\.irs\.gov/pub/irs-soi/(\d{2})in14(?:ar|acg)\.xls"
)
# Values SOI did not publish. The 2018 Form 1040 combined IRA distributions
# with pensions and annuities, so 2018 pensions are estimated from 2017 and
# 2019 (each file says how). The taxable estimate also uses the 2018 table.
SOI_ESTIMATED_VALUES = {
    ("taxable_pension_income.yaml", 2018),
    ("tax_exempt_pension_income.yaml", 2018),
}
# Values that were once keyed to the wrong tax year or misread from the table.
# IRS SOI Publication 1304 Table 1.4, all returns, thousands of dollars:
# partnership and S corporation net income less net loss (from tax year 2021
# the table splits partnerships from S corporations), social security benefits
# in total, and farm rental net income less net loss.
SOI_CORRECTED_VALUES = {
    "partnership_s_corp_income.yaml": {
        # 21in14ar: 469_816_308 - 168_152_043 + 766_681_240 - 92_689_104
        date(2021, 1, 1): 975_656_401_000,
        # 22in14ar: 487_094_509 - 175_602_300 + 812_741_318 - 93_025_607
        date(2022, 1, 1): 1_031_207_920_000,
    },
    "social_security.yaml": {
        date(2020, 1, 1): 774_017_713_000,
        date(2021, 1, 1): 791_161_174_000,
    },
    # 21in14ar: 6_186_997 - 631_042. The loss column's neighbour is the
    # number of returns with a loss (72_972).
    "farm_rent_income.yaml": {date(2021, 1, 1): 5_555_955_000},
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
    assert [reference["href"] for reference in parameter["metadata"]["reference"]] == [
        f"https://www.irs.gov/pub/irs-soi/{period.year % 100:02d}in14acg.xls"
        for period in sorted(values)
    ]


def test_soi_series_cite_the_table_for_each_tax_year():
    """Each SOI series value is for the tax year of its date and cites that
    year's Publication 1304 Table 1.4 or 1.4A file."""
    for path in sorted(SOI_DIR.glob("*.yaml")):
        parameter = yaml.safe_load(path.read_text())
        if "values" not in parameter:
            continue
        years = {period.year for period in parameter["values"]}
        cited = {
            2000 + int(match[1])
            for reference in parameter["metadata"]["reference"]
            if (match := SOI_TABLE_1_4_FILE.fullmatch(reference["href"]))
        }
        estimated = {year for name, year in SOI_ESTIMATED_VALUES if name == path.name}
        assert years - estimated <= cited, (path.name, sorted(years - cited))
        assert cited <= years, (path.name, sorted(cited - years))


def test_soi_corrected_values_hold_their_table_1_4_totals():
    for filename, anchors in SOI_CORRECTED_VALUES.items():
        values = yaml.safe_load((SOI_DIR / filename).read_text())["values"]
        for period, value in anchors.items():
            assert values[period] == value, (filename, period)


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
