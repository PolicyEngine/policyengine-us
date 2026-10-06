"""Pin the AR1000F line comments in the Arkansas gross income sources lists.

Each entry in gov.states.ar.tax.income.gross_income.sources.{joint,individual}
carries a "# Line N" comment naming the AR1000F income line it is reported on.
The form's numbering changed in tax year 2018, when Act 141 of 2017 added an
unemployment line and the uniformed services retirement exemption added a
military retirement line, so the 2015 block cannot reuse the 2018 numbers.

TY2015-2017 AR1000F (2015 booklet, form on #page=17, instructions on
#page=13 to #page=15; the 2016 and 2017 booklets number the lines the same way):
13 business income (Schedule C), 14 capital gains, 16 nonqualified IRA
distributions and taxable annuities, 17A/17B employer pensions and qualified
IRAs, where military retirement and disability retirement also go, 18 Schedule
E, 19 Schedule F, 20 other income (Form AR-OI, including gambling winnings).

TY2018+ AR1000F (2018 booklet, form on #page=15; 2022 and 2025 AR1000F,
#page=2): 13 business income, 14 capital gains, 16 nonqualified IRA
distributions, 17 military retirement (17A/17B on the 2018 form), 18A/18B
employer pensions and qualified IRAs, 19 Schedule E, 20 Schedule F,
21 unemployment, 22 other income.

The check reads the YAML text without importing the model, so it costs nothing.
A new source must be added to EXPECTED_LINES after checking the form.
"""

import re
from pathlib import Path

import pytest
import yaml


SOURCES = (
    Path(__file__).resolve().parents[2]
    / "parameters/gov/states/ar/tax/income/gross_income/sources"
)

TY2015_2017 = {
    "irs_employment_income": "8",
    "self_employment_income": "13",
    "sstb_self_employment_income": "13",
    "interest_income": "10",
    "dividend_income": "11",
    "alimony_income": "12",
    "ar_taxable_capital_gains": "14",
    "taxable_ira_distributions": "16",
    "taxable_roth_conversions": "16",
    "military_retirement_pay": "17A/17B",
    "taxable_pension_income": "17A/17B",
    "disability_benefits": "17A/17B",
    "rental_income": "18",
    "estate_income": "18",
    "farm_rent_income": "18",
    "farm_operations_income": "19",
    "gambling_winnings": "20",
}

TY2018_ON = {
    "irs_employment_income": "8",
    "self_employment_income": "13",
    "sstb_self_employment_income": "13",
    "interest_income": "10",
    "dividend_income": "11",
    "alimony_income": "12",
    "ar_taxable_capital_gains": "14",
    "taxable_ira_distributions": "16",
    "taxable_roth_conversions": "16",
    "military_retirement_pay": "17",
    "taxable_pension_income": "18A/18B",
    "taxable_401k_distributions": "18A/18B",
    "taxable_403b_distributions": "18A/18B",
    "taxable_sep_distributions": "18A/18B",
    "keogh_distributions": "18A/18B",
    "disability_benefits": "18A/18B",
    "rental_income": "19",
    "estate_income": "19",
    "farm_rent_income": "19",
    "farm_operations_income": "20",
    "unemployment_compensation": "21",
    "gambling_winnings": "22",
}

EXPECTED_LINES = {
    "2015-01-01": TY2015_2017,
    "2018-01-01": TY2018_ON,
    "2020-01-01": TY2018_ON,
    "2022-01-01": TY2018_ON,
}

PERIOD = re.compile(r"^\s*(\d{4}-\d{2}-\d{2}):\s*$")
ENTRY = re.compile(r"^\s*- (\w+)\s*(?:#\s*(.*))?$")
LINE = re.compile(r"^Line ([0-9A-Za-z/]+)")


def line_comments(path: Path) -> dict[str, list[tuple[str, str | None]]]:
    """Map each period in `path` to its (source, line label) entries."""
    blocks = {}
    period = None
    for text in path.read_text().splitlines():
        if text.startswith("metadata:"):
            break
        match = PERIOD.match(text)
        if match:
            period = match.group(1)
            blocks[period] = []
            continue
        match = ENTRY.match(text)
        if match and period is not None:
            source, comment = match.groups()
            label = LINE.match(comment or "")
            blocks[period].append((source, label.group(1) if label else None))
    return blocks


@pytest.mark.parametrize("file_name", ["joint.yaml", "individual.yaml"])
def test_ar_gross_income_sources_cite_the_form_line_for_their_year(file_name):
    path = SOURCES / file_name
    blocks = line_comments(path)
    # The text parse must see exactly the lists the parameter loader sees, so a
    # reformatted file cannot make this check pass with nothing to check.
    values = yaml.safe_load(path.read_text())["values"]
    assert {str(period): sources for period, sources in values.items()} == {
        period: [source for source, _ in entries] for period, entries in blocks.items()
    }
    assert sorted(blocks) == sorted(EXPECTED_LINES)
    errors = []
    for period, entries in blocks.items():
        expected = EXPECTED_LINES[period]
        for source, label in entries:
            key = re.sub(r"_(joint|indiv)$", "", source)
            if key not in expected:
                errors.append(
                    f"{period} {source}: not in EXPECTED_LINES; check the "
                    "AR1000F for that year and add it"
                )
            elif label is None:
                errors.append(
                    f"{period} {source}: no '# Line N' comment; the form has "
                    f"Line {expected[key]}"
                )
            elif label != expected[key]:
                errors.append(
                    f"{period} {source}: comment says Line {label}, the "
                    f"form has Line {expected[key]}"
                )
    assert not errors, "\n".join(errors)
