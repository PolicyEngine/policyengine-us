"""Invariants of the Medicare Part D low-income subsidy (``part_d_lis``).

The subsidy goes to Medicare enrollees in the 50 states and DC who are deemed
eligible (Medicaid enrollees, SSI recipients, people eligible for a Medicare
Savings Program) or whose countable income is below 150% of the poverty
guideline for their family size and whose countable resources are within the
limit plus $1,500 per person for burial funds (42 U.S.C. 1395w-114(a)(3); 42
CFR 423.773; 20 CFR 418 subpart D). Each enrollee in a Part D plan is valued
at the Medicare Trustees' average subsidy per subsidy enrollee, as CBO values
it.

Parameters:

1. Transcription: ``low_income_subsidy_per_recipient`` equals Table IV.B9's
   "Subsidy amount" (2026 report; the 2025 report for 2015; the 2023 report
   for 2013 and 2014).
2. Conservation: IV.B9 enrollment times the amount returns Table IV.B10's
   low-income subsidy payments, within the cells' rounding.
3. Differential: the same payments over Table V.B3's total enrollment equal
   ``part_d_low_income_subsidy_per_enrollee``, the series
   ``cbo_medicare_benefit`` subtracts, built from different cells.
4. Indexing: each resource limit is the previous year's limit raised by the
   September-to-September change in the CPI-U (not seasonally adjusted),
   never lowered, and rounded to the nearest $10, from the statute's 2006
   amounts, through 2027, the last year both Septembers are published. In
   2015 the couple limit is the formula's $24,260, not the $24,250 CMS
   printed (source-conflict candidate
   ``us:part-d-lis-couple-resource-limit-2015``). The Septembers typed here
   equal ``cpi_u_nsa_september`` wherever both have a value.
5. Projection: from 2028 each limit is the previous year's raised by the
   model's projected September CPI-U, never lowered, and rounded to $10. On
   a synthetic parameter tree, values in the YAML stand, published
   Septembers come first, a fall in the index leaves the limit unchanged,
   and a missing September sends both Septembers to the model's CPI-U
   series.
6. Rounding: the year-to-year adjustment reproduces CMS's published 2026
   limits from the unrounded ratio, and rounds an exact $5 up.
7. Bounds: the amount per recipient is positive and below Medicare spending
   per enrollee in every year from 2013, the spending series' first, to 2100.

Households (a seeded sample in one shared simulation, plus households at each
income and resource limit and just past it, each also run with more Social
Security, more interest and more assets):

8. Countable income equals the rule restated here: the couple's SSI income
   without interest and dividends, each source counted at no less than zero
   for each person, less $20 a month from unearned income (the rest from
   earnings), $65 a month of earnings and half the remaining earnings.
9. Interest and dividends never change countable income or eligibility.
10. More Social Security never lowers countable income or makes an income
    ineligible person income eligible; more assets never make a resource
    ineligible person resource eligible.
11. Eligibility equals the restated rule: family size counts the dependents
    on both returns when spouses file separately, and resources include the
    household's other real estate for the couple that holds it. Enrollees
    are the eligible people in a Part D plan who are on Medicaid or SSI or
    take the subsidy up, and the benefit is either zero or the year's amount
    per recipient, positive exactly for enrollees.
12. Spouses get the same countable income, family size and test results.
13. Reach: the sample reaches every branch the properties above check, so a
    change to the generator or the seed can't leave them vacuous.
14. Differential: for people without interest, dividends or rental income,
    countable income equals 12 times ``msp_countable_income``, which applies
    the same SSI exclusions through a separate formula (single people, and
    couples where both spouses are Medicare eligible). This checks how each
    formula gathers the couple's income; property 8 checks the exclusions
    themselves. The sample's states keep SSI's $20 general exclusion for the
    Medicare Savings Programs; Illinois and Mississippi exclude more under 42
    U.S.C. 1396a(r)(2), which the subsidy's income definition sets aside.
"""

from types import SimpleNamespace

import numpy as np
import pytest
from policyengine_core.parameters import ParameterNode

from policyengine_us import Simulation
from policyengine_us.parameters.uprating_extensions import (
    adjust_part_d_lis_resource_limit_for_inflation,
    extend_part_d_lis_resource_limits,
    get_september_cpi_u_values,
)
from policyengine_us.system import system

P = system.parameters
LIS = P.gov.hhs.medicare.part_d.low_income_subsidy
KINDS = ["individual", "couple"]

# 2026 Medicare Trustees Report (sha256 ffa56b91...8fa8), Table IV.B9 (file
# page 158): low-income subsidy enrollment (millions) and subsidy amount ($).
# 2015 from the 2025 report (sha256 1b3de7a4...4d95), Table IV.B9 (page 158);
# 2013 and 2014 from the 2023 report (sha256 89daaf29...fa67), Table IV.B9
# (page 158).
IV_B9 = {
    2013: (11.5, 2_023),
    2014: (11.8, 2_052),
    2015: (12.1, 2_112),
    2016: (12.4, 2_126),
    2017: (12.7, 2_156),
    2018: (12.9, 2_204),
    2019: (13.1, 2_273),
    2020: (13.1, 2_507),
    2021: (13.2, 2_646),
    2022: (13.7, 2_873),
    2023: (14.3, 3_092),
    2024: (14.5, 2_833),
    2025: (14.2, 1_226),
    2026: (14.4, 1_254),
    2027: (14.8, 1_384),
    2028: (15.2, 1_459),
    2029: (15.5, 1_579),
    2030: (15.8, 1_833),
    2031: (16.0, 1_922),
    2032: (16.2, 1_956),
    2033: (16.4, 1_982),
    2034: (16.6, 2_014),
    2035: (16.7, 2_076),
}
# Table IV.B10 (file page 159), low-income subsidy, $ billions, incurred;
# 2015 from the 2025 report's Table IV.B10 (page 159), 2013 and 2014 from the
# 2023 report's (page 159).
IV_B10 = {
    **{2013: 23.2, 2014: 24.3},
    **{2015: 25.6, 2016: 26.4, 2017: 27.3, 2018: 28.5, 2019: 29.7, 2020: 33.0},
    **{2021: 35.0, 2022: 39.4, 2023: 44.2, 2024: 41.2, 2025: 17.4, 2026: 18.1},
    **{2027: 20.5, 2028: 22.1, 2029: 24.5, 2030: 28.9, 2031: 30.7, 2032: 31.7},
    **{2033: 32.4, 2034: 33.3, 2035: 34.8},
}
# Table V.B3 (file page 196), total enrollment (HI and/or SMI), thousands;
# 2013 and 2014 from the 2021 report's Table V.B3 (sha256 ef3d1fa7...c8e,
# page 199), which the 2022 to 2026 reports drop.
V_B3_TOTAL = dict(
    zip(
        range(2013, 2036),
        (52_504, 54_115)
        + (55_589, 57_073, 58_683, 60_020, 61_535, 62_887, 63_980, 65_166)
        + (66_606, 68_066, 69_289, 70_743, 72_322, 74_026, 75_436, 76_598)
        + (77_521, 78_327, 79_058, 79_827, 80_632),
    )
)
# BLS CPI-U, U.S. city average, all items, not seasonally adjusted
# (CUUR0000SA0), September of each year, from the BLS public API: 2004 to
# 2025 retrieved 2026-10-11, 2026 retrieved 2026-11-08. pe-us's
# gov.bls.cpi.cpi_u_nsa_september starts in 2018; the years both hold must
# agree.
CPI_U_SEPTEMBER = {
    **{2004: 189.9, 2005: 198.8, 2006: 202.9, 2007: 208.490, 2008: 218.783},
    **{2009: 215.969, 2010: 218.439, 2011: 226.889, 2012: 231.407},
    **{2013: 234.149, 2014: 238.031, 2015: 237.945, 2016: 241.428},
    **{2017: 246.819, 2018: 252.439, 2019: 256.759, 2020: 260.280},
    **{2021: 274.310, 2022: 296.808, 2023: 307.789, 2024: 315.301},
    **{2025: 324.800, 2026: 336.940},
}
LAST_SEPTEMBER = max(CPI_U_SEPTEMBER)
STATUTE_2006 = {"individual": 10_000, "couple": 20_000}
# CMS, CY 2026 Resource and Cost-Sharing Limits for LIS (October 31, 2025),
# page 2, before the burial funds exclusion.
CMS_2025 = {"individual": 16_100, "couple": 32_130}
CMS_2026 = {"individual": 16_590, "couple": 33_100}


def _per_recipient(year):
    return P.calibration.gov.hhs.medicare.part_d.low_income_subsidy_per_recipient(
        f"{year}-01-01"
    )


def _limit(kind):
    return getattr(LIS.eligibility.resources.limit, kind)


def _round_to_10(x):
    return int(np.floor(x / 10 + 0.5)) * 10


@pytest.mark.parametrize("year", sorted(IV_B9))
def test_per_recipient_transcribes_table_iv_b9(year):
    assert _per_recipient(year) == IV_B9[year][1]


@pytest.mark.parametrize("year", sorted(IV_B9))
def test_enrollment_times_amount_returns_table_iv_b10(year):
    enrollment, amount = IV_B9[year]
    rebuilt = enrollment * 1e6 * _per_recipient(year) / 1e9
    # Rounding: total to $0.05B, enrollment to 0.05M x amount, amount to $0.5.
    tolerance = 0.05 + 0.05e6 * amount / 1e9 + 0.5 * enrollment * 1e6 / 1e9
    assert abs(rebuilt - IV_B10[year]) <= tolerance


@pytest.mark.parametrize("year", sorted(IV_B9))
def test_recipients_times_amount_matches_per_enrollee_series(year):
    per_enrollee = (
        P.calibration.gov.hhs.medicare.part_d_low_income_subsidy_per_enrollee(
            f"{year}-01-01"
        )
    )
    enrollment, _ = IV_B9[year]
    rebuilt = enrollment * 1e6 * _per_recipient(year) / (V_B3_TOTAL[year] * 1e3)
    # Enrollment rounded to 0.1 million is at worst 0.42% off (2015, 12.1).
    assert rebuilt == pytest.approx(per_enrollee, rel=0.005)


def test_typed_septembers_match_the_parameter():
    september = P.gov.bls.cpi.cpi_u_nsa_september
    # pe-us backdates each parameter's first value to 2015-01-01; only the
    # September instants are BLS values.
    years = [
        int(value.instant_str[:4])
        for value in september.values_list
        if value.instant_str.endswith("-09-01")
    ]
    assert LAST_SEPTEMBER in years
    for year in years:
        assert september(f"{year}-09-01") == pytest.approx(
            CPI_U_SEPTEMBER[year], abs=5e-4
        ), year


@pytest.mark.parametrize("kind", KINDS)
def test_resource_limits_follow_the_cpi_rule(kind):
    limit = _limit(kind)
    assert limit("2006-01-01") == STATUTE_2006[kind]
    for year in range(2007, LAST_SEPTEMBER + 2):
        growth = CPI_U_SEPTEMBER[year - 1] / CPI_U_SEPTEMBER[year - 2]
        expected = _round_to_10(limit(f"{year - 1}-01-01") * max(growth, 1))
        assert limit(f"{year}-01-01") == expected, year
        assert limit(f"{year}-07-01") == expected, year


@pytest.mark.parametrize("kind", KINDS)
def test_projected_resource_limits_follow_the_projected_cpi(kind):
    limit = _limit(kind)
    for year in range(LAST_SEPTEMBER + 2, 2101):
        prior, current = get_september_cpi_u_values(P.gov.bls.cpi, year)
        expected = _round_to_10(limit(f"{year - 1}-01-01") * max(current / prior, 1))
        assert limit(f"{year}-01-01") == expected, year
    # The projection is not flat over the Trustees' window.
    assert limit("2035-01-01") > limit(f"{LAST_SEPTEMBER + 1}-01-01")


def test_published_2026_limits_need_the_unrounded_ratio():
    # CMS reports the CY 2026 increase as 3.01%, but $16,100 x 1.0301 =
    # $16,584.61 rounds to $16,580; the unrounded ratio gives $16,585.04 and
    # the published $16,590. CMS's couple limits ($32,130 to $33,100) follow
    # the same rule; the model's couple limit builds on the formula's 2025
    # amount, $20 above CMS's (see the couple limit's parameter file).
    for kind in KINDS:
        assert (
            adjust_part_d_lis_resource_limit_for_inflation(
                CMS_2025[kind], 315.301, 324.800
            )
            == CMS_2026[kind]
        )
    assert _limit("individual")("2026-01-01") == CMS_2026["individual"]
    assert _limit("couple")("2026-01-01") == CMS_2026["couple"] + 20


@pytest.mark.parametrize(
    "prior_limit, prior, current, expected",
    [
        # 2015 couple: 23,860 x 238.031 / 234.149 = 24,255.58.
        (23_860, 234.149, 238.031, 24_260),
        # 2016: the index fell (237.945 < 238.031), so the limit stays.
        (24_260, 238.031, 237.945, 24_260),
        # An exact $5 rounds up.
        (1_005, 100.0, 100.0, 1_010),
        (1_000, 100.0, 100.5, 1_010),
        (1_000, 100.0, 100.4, 1_000),
    ],
)
def test_adjustment_rounds_to_the_nearest_10(prior_limit, prior, current, expected):
    assert (
        adjust_part_d_lis_resource_limit_for_inflation(prior_limit, prior, current)
        == expected
    )


def _synthetic_tree(nsa_septembers, sa_septembers):
    def values(data):
        return {"values": data}

    return ParameterNode(
        data={
            "gov": {
                "hhs": {
                    "medicare": {
                        "part_d": {
                            "low_income_subsidy": {
                                "eligibility": {
                                    "resources": {
                                        "limit": {
                                            "individual": values(
                                                {"2025-01-01": 16_100}
                                            ),
                                            "couple": values(
                                                {
                                                    "2025-01-01": 32_150,
                                                    "2026-01-01": 33_120,
                                                }
                                            ),
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "bls": {
                    "cpi": {
                        "cpi_u_nsa_september": values(nsa_septembers),
                        "cpi_u": values(sa_septembers),
                    }
                },
            }
        }
    )


def test_extension_on_a_synthetic_tree():
    nsa = {"2024-09-01": 315.301, "2025-09-01": 324.8, "2026-09-01": 336.94}
    nsa["2027-09-01"] = 330.0  # a fall
    nsa["2028-09-01"] = 340.0
    # The model's (seasonally adjusted) series differs from the published one,
    # so a year that reads it shows which series it used.
    sa = {date: 0.99 * value for date, value in nsa.items()}
    sa["2029-09-01"] = 0.99 * 350.0
    parameters = _synthetic_tree(nsa, sa)
    extend_part_d_lis_resource_limits(parameters, end_year=2031)
    limits = parameters.gov.hhs.medicare.part_d.low_income_subsidy.eligibility
    limits = limits.resources.limit
    individual = {y: limits.individual(f"{y}-01-01") for y in range(2025, 2036)}
    couple = {y: limits.couple(f"{y}-01-01") for y in range(2025, 2036)}
    # 2026: published Septembers 2024 and 2025; the YAML's 2026 couple stands.
    assert individual[2026] == 16_590
    assert couple[2026] == 33_120
    # 2027: published 2025 and 2026.
    assert individual[2027] == _round_to_10(16_590 * 336.94 / 324.8)
    assert couple[2027] == _round_to_10(33_120 * 336.94 / 324.8)
    # 2028: the published index fell, so the limits stay.
    assert individual[2028] == individual[2027]
    assert couple[2028] == couple[2027]
    # 2029: published 2027 and 2028.
    assert individual[2029] == _round_to_10(individual[2028] * 340.0 / 330.0)
    # 2030: September 2029 is not published, so both Septembers come from
    # the model's series (0.99 x 350 / (0.99 x 340), not 0.99 x 350 / 340).
    assert individual[2030] == _round_to_10(individual[2029] * 350.0 / 340.0)
    # 2031: the model's series holds flat after its last month.
    assert individual[2031] == individual[2030]
    # After the end year the last value holds.
    assert individual[2035] == individual[2031]
    assert couple[2035] == couple[2031]


def test_amount_positive_and_below_spending():
    for year in range(2013, 2101):
        amount = _per_recipient(year)
        spending = P.calibration.gov.hhs.medicare.per_capita_cost(f"{year}-01-01")
        assert 0 < amount < spending, year


# Households.
YEAR = 2026
N = 300
SEED = 20261011
STATES = ["TX", "CA", "NY", "AK", "HI", "FL", "PR", "DC"]
VARIANTS = ["base", "more_ss", "more_interest", "more_assets"]
LIMITS = LIS.eligibility.resources(f"{YEAR}-01-01")
BURIAL = LIMITS.burial_exclusion


def _random_households():
    rng = np.random.default_rng(SEED)
    # Features added after the first sample come from their own generator,
    # so the original draws stay the same.
    extra = np.random.default_rng(SEED + 1)
    out = []
    for _ in range(N):
        married = bool(rng.random() < 0.5)

        def person():
            return dict(
                social_security=int(rng.choice([0, 6_000, 12_000, 18_000, 26_000])),
                employment_income=int(rng.choice([0, 0, 0, 4_000, 15_000])),
                interest_income=int(rng.choice([0, 0, 300, 4_000])),
                dividend_income=int(rng.choice([0, 0, 1_000])),
                bank_account_assets=int(rng.choice([0, 3_000, 9_000, 16_000, 40_000])),
                stock_assets=int(rng.choice([0, 0, 5_000])),
                medicare_enrolled=bool(rng.random() < 0.9),
                medicaid_enrolled=bool(rng.random() < 0.15),
                ssi=int(rng.choice([0, 0, 0, 0, 2_400])),
                msp_eligible=bool(rng.random() < 0.15),
                takes_up_part_d_lis_if_eligible=bool(rng.random() < 0.7),
                takes_up_medicare_part_d_if_eligible=bool(rng.random() < 0.85),
                rental_income=int(extra.choice([0, 0, 0, -6_000, 2_400])),
            )

        out.append(
            dict(
                state=str(rng.choice(STATES)),
                dependents=int(rng.choice([0, 0, 0, 1, 2])),
                members=[person()] + ([person()] if married else []),
                separate=married and bool(extra.random() < 0.3),
                real_estate=int(extra.choice([0, 0, 0, 6_000, 60_000])),
            )
        )
    return out


def _boundary_households():
    # Not deemed, in a Part D plan, taking the subsidy up, in Texas.
    def person(social_security, bank_account_assets=0):
        return dict(
            social_security=social_security,
            employment_income=0,
            interest_income=0,
            dividend_income=0,
            bank_account_assets=bank_account_assets,
            stock_assets=0,
            medicare_enrolled=True,
            medicaid_enrolled=False,
            ssi=0,
            msp_eligible=False,
            takes_up_part_d_lis_if_eligible=True,
            takes_up_medicare_part_d_if_eligible=True,
            rental_income=0,
        )

    def household(members, real_estate=0):
        return dict(
            state="TX",
            dependents=0,
            members=members,
            separate=False,
            real_estate=real_estate,
        )

    single = LIMITS.limit.individual + BURIAL
    couple = LIMITS.limit.couple + 2 * BURIAL
    single_income = 1.5 * _fpg("TX", 1)
    couple_income = 1.5 * _fpg("TX", 2)
    out = []
    for over in (0, 1):
        out.append(household([person(6_000, single + over)]))
        out.append(
            household([person(6_000, couple - 9_000 + over), person(6_000, 9_000)])
        )
        out.append(household([person(6_000, single - 10_000 + over)], 10_000))
        # Countable income at 150% of the guideline, and $12 a year below.
        out.append(household([person(int(single_income + 240 - 12 * (1 - over)))]))
        out.append(
            household(
                [
                    person(20_000),
                    person(int(couple_income + 240 - 20_000 - 12 * (1 - over))),
                ]
            )
        )
    return out


def _fpg(state, size):
    fpg = P.gov.hhs.fpg(f"{YEAR}-01-01")
    group = state if state in ("AK", "HI", "PR") else "CONTIGUOUS_US"
    return fpg.first_person[group] + fpg.additional_person[group] * (size - 1)


HOUSEHOLDS = _random_households() + _boundary_households()


def _variant(member, variant, is_head):
    member = dict(member)
    if is_head and variant == "more_ss":
        member["social_security"] += 3_000
    if is_head and variant == "more_interest":
        member["interest_income"] += 5_000
        member["dividend_income"] += 2_000
    if is_head and variant == "more_assets":
        member["bank_account_assets"] += 5_000
    return member


INCOME_INPUTS = (
    "social_security",
    "employment_income",
    "interest_income",
    "dividend_income",
    "rental_income",
)


def _situation(households, variants, inputs=True):
    people, marital_units, tax_units, spm_units, units = {}, {}, {}, {}, {}
    rows = []  # (household index, variant, member index, person name)
    for v in variants:
        for i, h in enumerate(households):
            names = []
            for j, member in enumerate(h["members"]):
                name = f"{v}_{i}_{j}"
                record = _variant(member, v, j == 0)
                if not inputs:
                    record = {k: record[k] for k in INCOME_INPUTS}
                people[name] = {
                    "age": {YEAR: 70},
                    **{k: {YEAR: val} for k, val in record.items()},
                }
                names.append(name)
                rows.append((i, v, j, name))
            spouses = list(names)
            returns = [[name] for name in spouses] if h["separate"] else [list(spouses)]
            dependents = []
            for k in range(h["dependents"]):
                name = f"{v}_{i}_d{k}"
                people[name] = {
                    "age": {YEAR: 10},
                    "is_tax_unit_dependent": {YEAR: True},
                }
                marital_units[f"mu_{name}"] = {"members": [name]}
                # Spouses who file separately claim the dependents in turn.
                returns[k % len(returns)].append(name)
                dependents.append(name)
            marital_units[f"mu_{v}_{i}"] = {"members": spouses}
            for r, members in enumerate(returns):
                tax_units[f"tu_{v}_{i}_{r}"] = {"members": members}
            members = spouses + dependents
            spm_units[f"spm_{v}_{i}"] = {"members": members}
            units[f"hh_{v}_{i}"] = {
                "members": members,
                "state_code": {YEAR: h["state"]},
                "household_other_real_estate_equity": {YEAR: h["real_estate"]},
            }
    situation = {
        "people": people,
        "marital_units": marital_units,
        "tax_units": tax_units,
        "spm_units": spm_units,
        "households": units,
    }
    return situation, rows


@pytest.fixture(scope="module")
def sample():
    situation, rows = _situation(HOUSEHOLDS, VARIANTS)
    sim = Simulation(situation=situation)
    names = list(situation["people"])
    index = {name: k for k, name in enumerate(names)}
    variables = [
        "part_d_lis",
        "part_d_lis_enrolled",
        "part_d_lis_eligible",
        "part_d_lis_deemed_eligible",
        "part_d_lis_income_eligible",
        "part_d_lis_resource_eligible",
        "part_d_lis_countable_income",
        "part_d_lis_family_size",
    ]
    values = {v: sim.calculate(v, YEAR) for v in variables}
    return rows, index, values


def _restated_countable(members, floor_sources=True):
    def unearned(m):
        rent = max(m["rental_income"], 0) if floor_sources else m["rental_income"]
        return m["social_security"] + rent

    earned = sum(m["employment_income"] for m in members) / 12
    total_unearned = sum(unearned(m) for m in members) / 12
    general = min(20, max(total_unearned, 0))
    countable_unearned = max(total_unearned, 0) - general
    countable_earned = max(earned - 65 - (20 - general), 0) / 2
    return 12 * (countable_unearned + countable_earned)


def _restated_tests(h, members, real_estate=True):
    """Family size, income test and resource test for the household's couple."""
    couple = len(members)
    size = couple + h["dependents"]
    income_ok = _restated_countable(members) < 1.5 * _fpg(h["state"], size)
    resources = sum(m["bank_account_assets"] + m["stock_assets"] for m in members)
    # Every adult is 70 and every dependent 10, so the couple holds the
    # household's real estate.
    resources += h["real_estate"] if real_estate else 0
    limit = LIMITS.limit.couple if couple == 2 else LIMITS.limit.individual
    resource_ok = resources <= limit + BURIAL * couple
    return size, income_ok, resource_ok, resources - (limit + BURIAL * couple)


def _value(values, index, variable, name):
    return values[variable][index[name]]


def _members(i, v):
    return [_variant(m, v, j == 0) for j, m in enumerate(HOUSEHOLDS[i]["members"])]


def test_countable_income_matches_restated_rule(sample):
    rows, index, values = sample
    for i, v, _, name in rows:
        expected = _restated_countable(_members(i, v))
        actual = _value(values, index, "part_d_lis_countable_income", name)
        assert actual == pytest.approx(expected, abs=0.01), (i, v)


def test_interest_and_dividends_change_nothing(sample):
    rows, index, values = sample
    for i, v, j, name in rows:
        if v != "more_interest":
            continue
        base = f"base_{i}_{j}"
        for variable in [
            "part_d_lis_countable_income",
            "part_d_lis_income_eligible",
            "part_d_lis_eligible",
            "part_d_lis",
        ]:
            assert _value(values, index, variable, name) == _value(
                values, index, variable, base
            ), (i, variable)


def test_more_income_or_assets_never_helps(sample):
    rows, index, values = sample
    for i, v, j, name in rows:
        base = f"base_{i}_{j}"
        if v == "more_ss":
            assert _value(values, index, "part_d_lis_countable_income", name) >= (
                _value(values, index, "part_d_lis_countable_income", base)
            )
            if _value(values, index, "part_d_lis_income_eligible", name):
                assert _value(values, index, "part_d_lis_income_eligible", base), i
        if v == "more_assets":
            if _value(values, index, "part_d_lis_resource_eligible", name):
                assert _value(values, index, "part_d_lis_resource_eligible", base), i


def _restated_enrollment(h, me, income_ok, resource_ok):
    excluded = list(LIS.eligibility.ineligible_jurisdictions(f"{YEAR}-01-01"))
    deemed = me["medicaid_enrolled"] or me["ssi"] > 0 or me["msp_eligible"]
    eligible = (
        me["medicare_enrolled"]
        and h["state"] not in excluded
        and (deemed or (income_ok and resource_ok))
    )
    automatic = me["medicaid_enrolled"] or me["ssi"] > 0
    in_part_d = me["takes_up_medicare_part_d_if_eligible"]
    takes_up = me["takes_up_part_d_lis_if_eligible"]
    enrolled = eligible and in_part_d and (automatic or takes_up)
    return deemed, eligible, enrolled


def test_eligibility_and_benefit_match_restated_rules(sample):
    rows, index, values = sample
    amount = _per_recipient(YEAR)
    for i, v, j, name in rows:
        h = HOUSEHOLDS[i]
        members = _members(i, v)
        size, income_ok, resource_ok, _ = _restated_tests(h, members)
        _, eligible, enrolled = _restated_enrollment(
            h, members[j], income_ok, resource_ok
        )
        assert _value(values, index, "part_d_lis_family_size", name) == size, i
        assert _value(values, index, "part_d_lis_income_eligible", name) == income_ok
        assert _value(values, index, "part_d_lis_resource_eligible", name) == (
            resource_ok
        ), i
        assert _value(values, index, "part_d_lis_eligible", name) == eligible, i
        assert _value(values, index, "part_d_lis_enrolled", name) == enrolled, i
        benefit = _value(values, index, "part_d_lis", name)
        assert benefit == (amount if enrolled else 0), i


def test_spouses_agree(sample):
    rows, index, values = sample
    for i, v, j, name in rows:
        if j != 1:
            continue
        head = f"{v}_{i}_0"
        for variable in [
            "part_d_lis_countable_income",
            "part_d_lis_family_size",
            "part_d_lis_income_eligible",
            "part_d_lis_resource_eligible",
        ]:
            assert _value(values, index, variable, name) == _value(
                values, index, variable, head
            ), (i, variable)


def test_sample_reaches_every_branch():
    counts = dict.fromkeys(
        [
            "couple",
            "dependents",
            "territory",
            "no_medicare",
            "deemed_by_medicaid_only",
            "deemed_by_ssi_only",
            "deemed_by_msp_only",
            "passes_both_tests",
            "fails_only_resources",
            "fails_only_income",
            "eligible_without_part_d",
            "eligible_not_taking_up",
            "automatic_despite_no_take_up",
            "enrolled",
            "on_resource_limit",
            "one_dollar_over_resource_limit",
            "on_income_limit",
            "separate_returns_split_dependents",
            "split_dependents_change_income_test",
            "rental_floor_changes_income_test",
            "real_estate_changes_resource_test",
        ],
        0,
    )
    for i, h in enumerate(HOUSEHOLDS):
        members = _members(i, "base")
        size, income_ok, resource_ok, over = _restated_tests(h, members)
        counts["couple"] += len(members) == 2
        counts["dependents"] += h["dependents"] > 0
        counts["territory"] += h["state"] == "PR"
        counts["on_resource_limit"] += over == 0
        counts["one_dollar_over_resource_limit"] += over == 1
        countable = _restated_countable(members)
        counts["on_income_limit"] += countable == 1.5 * _fpg(h["state"], size)
        if h["separate"] and h["dependents"] == 1:
            counts["separate_returns_split_dependents"] += 1
            own_return = _restated_countable(members) < 1.5 * _fpg(h["state"], size - 1)
            counts["split_dependents_change_income_test"] += own_return != income_ok
        netted = _restated_countable(members, floor_sources=False)
        counts["rental_floor_changes_income_test"] += income_ok != (
            netted < 1.5 * _fpg(h["state"], size)
        )
        without = _restated_tests(h, members, real_estate=False)[2]
        counts["real_estate_changes_resource_test"] += without != resource_ok
        for me in members:
            counts["no_medicare"] += not me["medicare_enrolled"]
            routes = [me["medicaid_enrolled"], me["ssi"] > 0, me["msp_eligible"]]
            if sum(routes) == 1:
                counts["deemed_by_medicaid_only"] += routes[0]
                counts["deemed_by_ssi_only"] += routes[1]
                counts["deemed_by_msp_only"] += routes[2]
            counts["passes_both_tests"] += income_ok and resource_ok
            counts["fails_only_resources"] += income_ok and not resource_ok
            counts["fails_only_income"] += resource_ok and not income_ok
            _, eligible, enrolled = _restated_enrollment(h, me, income_ok, resource_ok)
            in_part_d = me["takes_up_medicare_part_d_if_eligible"]
            automatic = me["medicaid_enrolled"] or me["ssi"] > 0
            takes_up = me["takes_up_part_d_lis_if_eligible"]
            counts["eligible_without_part_d"] += eligible and not in_part_d
            counts["eligible_not_taking_up"] += (
                eligible and in_part_d and not automatic and not takes_up
            )
            counts["automatic_despite_no_take_up"] += (
                eligible and in_part_d and automatic and not takes_up
            )
            counts["enrolled"] += enrolled
    unreached = [branch for branch, count in counts.items() if count == 0]
    assert not unreached, counts


def test_countable_income_matches_msp_countable_income():
    # No interest, dividends or rental income, everyone 70 and so Medicare
    # eligible: the MSP formula then counts the same income the same way,
    # through its couple branch for married couples and its personal branch
    # otherwise.
    households = [
        {
            **h,
            "members": [
                {**m, "interest_income": 0, "dividend_income": 0, "rental_income": 0}
                for m in h["members"]
            ],
        }
        for h in HOUSEHOLDS
    ]
    situation, rows = _situation(households, ["base"], inputs=False)
    sim = Simulation(situation=situation)
    names = list(situation["people"])
    lis = sim.calculate("part_d_lis_countable_income", YEAR)
    msp = sim.calculate("msp_countable_income", f"{YEAR}-01")
    medicare_eligible = sim.calculate("is_medicare_eligible", YEAR)
    adults = np.array([not name.split("_")[-1].startswith("d") for name in names])
    assert medicare_eligible[adults].all()
    np.testing.assert_allclose(lis[adults], 12 * msp[adults], atol=0.01)
