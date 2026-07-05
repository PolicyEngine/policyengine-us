"""Pin state parameters that were frozen by a misplaced (sibling-of-``values``)
``uprating:`` block, to explicit values from official published sources.

These parameters previously stopped at their last hand-entered year because the
``uprating:`` block sat beside ``values:`` (not under ``metadata:``) and was
silently discarded by the loader (see policyengine-us #8905). The fix adds
explicit dated entries from each state's official annual release. Several of the
parameters are not (currently) reachable through a household calculation -- e.g.
New York's itemized-deduction ``phase_out.start`` is not referenced by any
formula -- so they are pinned here rather than in a YAML household test.

Sources (one per state; see the parameter YAML ``reference`` blocks for the rest):
  * NE -- 2026 Nebraska Estimated Income Tax Rate Schedule (Form 1040N-ES,
    8-014-2025 Rev. 11-2025), page 5.
  * ME -- Maine Revenue Services 2026 Individual Income Tax Rate Schedules
    (rev. May 5, 2026) and the 2026 Estimated Tax Worksheet phase-out worksheets
    (rev. Dec. 2025).
  * RI -- RI Division of Taxation Advisory ADV 2025-22 (Nov. 3, 2025).
  * NY -- Form IT-196-I "Table 1" applicable amounts, tax years 2024 and 2025.
"""

import pytest

from policyengine_us import CountryTaxBenefitSystem

SYSTEM = CountryTaxBenefitSystem()


def _p(date):
    return SYSTEM.parameters(date)


# --- Nebraska: 2026 indexed bracket thresholds (Neb. Rev. Stat. 77-2715.03) ----
# brackets[1..3] map to the 3.51%/4.55%/4.55% breakpoints in the 2026 schedule.
NE_2026 = {
    "single": (4_130, 24_760, 39_900),
    "separate": (4_130, 24_760, 39_900),
    "head_of_household": (7_700, 39_620, 59_160),
    "joint": (8_250, 49_530, 79_800),
    "surviving_spouse": (8_250, 49_530, 79_800),
}


@pytest.mark.parametrize("status,thresholds", NE_2026.items())
def test_ne_2026_income_tax_brackets(status, thresholds):
    # Access the raw parameter tree (not parameters(date)) so the bracket scale is
    # not collapsed to an instant, then evaluate each threshold at the 2026 date.
    rates = getattr(SYSTEM.parameters.gov.states.ne.tax.income.rates, status)
    got = tuple(rates.brackets[i].threshold("2026-01-01") for i in (1, 2, 3))
    assert got == thresholds


# --- Maine: 2026 indexed rate-schedule thresholds (36 M.R.S. 5111 / 5403) ------
# brackets[1] = 6.75% start, brackets[2] = 7.15% start.
ME_MAIN_2026 = {
    "single": (27_400, 64_850),
    "separate": (27_400, 64_850),
    "head_of_household": (41_100, 97_300),
    "joint": (54_850, 129_750),
    "surviving_spouse": (54_850, 129_750),
}


@pytest.mark.parametrize("status,thresholds", ME_MAIN_2026.items())
def test_me_2026_income_tax_brackets(status, thresholds):
    main = getattr(SYSTEM.parameters.gov.states.me.tax.income.main, status)
    got = tuple(main.brackets[i].threshold("2026-01-01") for i in (1, 2))
    assert got == thresholds


# --- Maine: 2026 standard/itemized deduction phase-out start (36 M.R.S. 5124-C/5125)
ME_DED_PHASEOUT_2026 = {
    "SINGLE": 102_250,
    "SEPARATE": 102_250,
    "HEAD_OF_HOUSEHOLD": 153_400,
    "JOINT": 204_550,
    "SURVIVING_SPOUSE": 204_550,
}


@pytest.mark.parametrize("status,value", ME_DED_PHASEOUT_2026.items())
def test_me_2026_deduction_phaseout_start(status, value):
    start = _p("2026-01-01").gov.states.me.tax.income.deductions.phase_out.start
    assert start[status] == value


# --- Maine: 2026 personal exemption phase-out start (36 M.R.S. 5126-A / 5403) ---
ME_PE_PHASEOUT_2026 = {
    "SINGLE": 341_000,
    "SEPARATE": 204_575,
    "HEAD_OF_HOUSEHOLD": 375_050,
    "JOINT": 409_150,
    "SURVIVING_SPOUSE": 409_150,
}


@pytest.mark.parametrize("status,value", ME_PE_PHASEOUT_2026.items())
def test_me_2026_personal_exemption_phaseout_start(status, value):
    node = _p(
        "2026-01-01"
    ).gov.states.me.tax.income.deductions.personal_exemption.phaseout.start
    assert node[status] == value


# --- Rhode Island: 2026 standard deduction (R.I. Gen. Laws 44-30-2.6) ----------
RI_STD_2026 = {
    "SINGLE": 11_200,
    "JOINT": 22_400,
    "HEAD_OF_HOUSEHOLD": 16_800,
    "SEPARATE": 11_200,
    "SURVIVING_SPOUSE": 22_400,
}


@pytest.mark.parametrize("status,value", RI_STD_2026.items())
def test_ri_2026_standard_deduction(status, value):
    amount = _p("2026-01-01").gov.states.ri.tax.income.deductions.standard.amount
    assert amount[status] == value


# --- New York: 2024 and 2025 itemized-deduction phase-out applicable amount ----
# NY Tax Law 615 conforms to the pre-TCJA federal 26 U.S.C. 68 applicable amount,
# which NY continues to inflation-adjust. This parameter is not currently consumed
# by any formula, so it is pinned here rather than in a household test.
NY_ITEMIZED_START = {
    "2024-01-01": {
        "SINGLE": 330_200,
        "JOINT": 396_250,
        "SURVIVING_SPOUSE": 396_250,
        "SEPARATE": 198_100,
        "HEAD_OF_HOUSEHOLD": 363_250,
    },
    "2025-01-01": {
        "SINGLE": 340_700,
        "JOINT": 408_850,
        "SURVIVING_SPOUSE": 408_850,
        "SEPARATE": 204_400,
        "HEAD_OF_HOUSEHOLD": 374_800,
    },
}


@pytest.mark.parametrize("date", list(NY_ITEMIZED_START))
def test_ny_itemized_phase_out_start(date):
    node = _p(date).gov.states.ny.tax.income.deductions.itemized.phase_out.start
    for status, value in NY_ITEMIZED_START[date].items():
        assert node[status] == value, f"{status} @ {date}"
