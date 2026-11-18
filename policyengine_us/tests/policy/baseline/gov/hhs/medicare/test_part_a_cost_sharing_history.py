"""Medicare Part A premiums and inpatient hospital deductible: an announced
amount for every modeled year, rounded as the statute requires.

CMS announces each calendar year's Part A premiums and inpatient hospital
deductible in the Federal Register. CountryTaxBenefitSystem backdates each
parameter's earliest value to FIRST_MODELED_YEAR, so a file whose values start
after that year silently applies a later year's amount to earlier years. For
each of the three parameter files:

- the values take effect on January 1 of every year from FIRST_MODELED_YEAR
  through the last announced year, with no gaps.

For every announced year:

- the full premium is a whole number of dollars (42 U.S.C. 1395i-2(d)(2));
- the reduced premium, for 30 to 39 quarters of coverage, is the full premium
  reduced by 45 percent (1395i-2(d)(4)(A)) and rounded to the nearest dollar,
  half up. CMS reduces the rounded full premium: for 2022 the unrounded rate of
  $499.29 would give $275, but the notice (86 FR 64214) sets $274, which is
  55 percent of $499;
- the deductible is a multiple of $4 (42 U.S.C. 1395e(b)(1)).

The parameter files are read directly, since the loaded parameters already
include the backdated values. The announced years are a small finite set, so
each test checks all of them.
"""

from datetime import date
from pathlib import Path

import pytest
import yaml

import policyengine_us
from policyengine_us.tools.parameters import FIRST_MODELED_YEAR

PART_A = Path(policyengine_us.__file__).parent / "parameters/gov/hhs/medicare/part_a"
FILES = ["full_premium", "reduced_premium", "deductible"]


def announced(name):
    """{year: amount} for each value dated in the parameter file."""
    values = yaml.safe_load((PART_A / f"{name}.yaml").read_text())["values"]
    assert all(instant == date(instant.year, 1, 1) for instant in values)
    return {instant.year: amount for instant, amount in values.items()}


FULL = announced("full_premium")
REDUCED = announced("reduced_premium")
DEDUCTIBLE = announced("deductible")


@pytest.mark.parametrize("name", FILES)
def test_every_modeled_year_has_an_announced_amount(name):
    years = announced(name)
    missing = set(range(FIRST_MODELED_YEAR, max(years) + 1)) - set(years)
    assert not missing, f"{name} backdates a later amount to {sorted(missing)}"


@pytest.mark.parametrize("year", sorted(FULL))
def test_full_premium_is_whole_dollars(year):
    assert float(FULL[year]).is_integer()


def test_premiums_are_announced_for_the_same_years():
    assert FULL.keys() == REDUCED.keys()


@pytest.mark.parametrize("year", sorted(REDUCED))
def test_reduced_premium_is_45_percent_off_the_full_premium(year):
    # 55 percent of the full premium in cents, rounded half up to the dollar.
    assert REDUCED[year] == (55 * int(FULL[year]) + 50) // 100


@pytest.mark.parametrize("year", sorted(DEDUCTIBLE))
def test_deductible_is_a_multiple_of_4(year):
    assert DEDUCTIBLE[year] % 4 == 0
