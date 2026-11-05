"""Invariants of the Medicare Part D low-income subsidy (``part_d_lis``).

The subsidy goes to Medicare enrollees in the 50 states and DC who are deemed
eligible (Medicaid enrollees, SSI recipients, Medicare Savings Program
enrollees) or whose countable income is below 150% of the poverty guideline
for their family size and whose countable resources are within the limit
plus $1,500 per person for burial funds (42 U.S.C. 1395w-114(a)(3); 42 CFR
423.773; 20 CFR 418 subpart D). Each enrollee is valued at the Medicare
Trustees' average subsidy per subsidy enrollee, as CBO does.

Parameters:

1. Transcription: ``low_income_subsidy_per_recipient`` equals Table IV.B9's
   "Subsidy amount" (2026 report; the 2025 report for 2015).
2. Conservation: IV.B9 enrollment times the amount returns Table IV.B10's
   low-income subsidy payments, within the cells' rounding.
3. Differential: the same payments over Table V.B3's total enrollment equal
   ``part_d_low_income_subsidy_per_enrollee``, the series
   ``cbo_medicare_benefit`` subtracts, built from different cells.
4. Indexing: each resource limit is the previous year's limit raised by the
   September-to-September change in the CPI-U (not seasonally adjusted),
   never lowered, and rounded to the nearest $10, from the statute's 2006
   amounts. SSA's published 2015 couple limit is $10 below the rule; the
   parameter keeps the published amount (an intended exception).
5. Bounds (Hypothesis): the amount per recipient is positive and below
   Medicare spending per enrollee, and the limits never fall, in every year
   from 2015 to 2100.

Households (a seeded sample in one shared simulation, each household also
run with more Social Security, more interest and more assets):

6. Countable income equals the rule restated here: the couple's SSI
   income without interest and dividends, less $20 a month from unearned
   income (the rest from earnings), $65 a month of earnings and half the
   remaining earnings.
7. Interest and dividends never change countable income or eligibility.
8. More Social Security never lowers countable income or makes an income
   ineligible person income eligible; more assets never make a resource
   ineligible person resource eligible.
9. Eligibility equals the restated rule, and the benefit is either zero or
   the year's amount per recipient, positive exactly for enrollees, who
   are all eligible.
10. Spouses get the same countable income, family size and test results.
11. Differential: for people without interest or dividends, countable income
    equals 12 times ``msp_countable_income``, which applies the same SSI
    exclusions through a separate formula (single people, and couples where
    both spouses are Medicare eligible).
"""

import numpy as np
import pytest
from hypothesis import given
from hypothesis import strategies as st

from policyengine_us import Simulation
from policyengine_us.system import system

P = system.parameters
PER_RECIPIENT = "calibration.gov.hhs.medicare.part_d.low_income_subsidy_per_recipient"
LIS = P.gov.hhs.medicare.part_d.low_income_subsidy

# 2026 Medicare Trustees Report (sha256 ffa56b91...8fa8), Table IV.B9 (file
# page 158): low-income subsidy enrollment (millions) and subsidy amount ($).
# 2015 from the 2025 report (sha256 1b3de7a4...4d95), Table IV.B9 (page 158).
IV_B9 = {
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
# 2015 from the 2025 report's Table IV.B10 (page 159).
IV_B10 = {
    **{2015: 25.6, 2016: 26.4, 2017: 27.3, 2018: 28.5, 2019: 29.7, 2020: 33.0},
    **{2021: 35.0, 2022: 39.4, 2023: 44.2, 2024: 41.2, 2025: 17.4, 2026: 18.1},
    **{2027: 20.5, 2028: 22.1, 2029: 24.5, 2030: 28.9, 2031: 30.7, 2032: 31.7},
    **{2033: 32.4, 2034: 33.3, 2035: 34.8},
}
# Table V.B3 (file page 196), total enrollment (HI and/or SMI), thousands.
V_B3_TOTAL = dict(
    zip(
        range(2015, 2036),
        (55_589, 57_073, 58_683, 60_020, 61_535, 62_887, 63_980, 65_166)
        + (66_606, 68_066, 69_289, 70_743, 72_322, 74_026, 75_436, 76_598)
        + (77_521, 78_327, 79_058, 79_827, 80_632),
    )
)
# BLS CPI-U, U.S. city average, all items, not seasonally adjusted
# (CUUR0000SA0), September of each year, retrieved 2026-10-11 from the BLS
# public API. (pe-us's gov.bls.cpi.cpi_u holds seasonally adjusted values
# from 2024, so it is not used here.)
CPI_U_SEPTEMBER = {
    **{2004: 189.9, 2005: 198.8, 2006: 202.9, 2007: 208.490, 2008: 218.783},
    **{2009: 215.969, 2010: 218.439, 2011: 226.889, 2012: 231.407},
    **{2013: 234.149, 2014: 238.031, 2015: 237.945, 2016: 241.428},
    **{2017: 246.819, 2018: 252.439, 2019: 256.759, 2020: 260.280},
    **{2021: 274.310, 2022: 296.808, 2023: 307.789, 2024: 315.301},
    **{2025: 324.800},
}
STATUTE_2006 = {"individual": 10_000, "couple": 20_000}
PUBLISHED_EXCEPTIONS = {("couple", 2015): 24_250}  # the rule gives 24,260


def _per_recipient(year):
    return P.calibration.gov.hhs.medicare.part_d.low_income_subsidy_per_recipient(
        f"{year}-01-01"
    )


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


def _round_to_10(x):
    return int(np.floor(x / 10 + 0.5)) * 10


@pytest.mark.parametrize("kind", ["individual", "couple"])
def test_resource_limits_follow_the_cpi_rule(kind):
    limit = getattr(LIS.eligibility.resources.limit, kind)
    assert limit("2006-01-01") == STATUTE_2006[kind]
    for year in range(2007, 2027):
        growth = CPI_U_SEPTEMBER[year - 1] / CPI_U_SEPTEMBER[year - 2]
        expected = _round_to_10(limit(f"{year - 1}-01-01") * max(growth, 1))
        expected = PUBLISHED_EXCEPTIONS.get((kind, year), expected)
        assert limit(f"{year}-01-01") == expected, year


@given(st.integers(2015, 2100))
def test_amount_positive_and_below_spending(year):
    amount = _per_recipient(year)
    spending = P.calibration.gov.hhs.medicare.per_capita_cost(f"{year}-01-01")
    assert 0 < amount < spending


@given(st.integers(2007, 2100))
def test_resource_limits_never_fall(year):
    for kind in ["individual", "couple"]:
        limit = getattr(LIS.eligibility.resources.limit, kind)
        assert limit(f"{year}-01-01") >= limit(f"{year - 1}-01-01")


# Households.
YEAR = 2026
N = 300
SEED = 20261011
STATES = ["TX", "CA", "NY", "AK", "HI", "FL", "PR", "DC"]
VARIANTS = ["base", "more_ss", "more_interest", "more_assets"]


def _households():
    rng = np.random.default_rng(SEED)
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
            )

        out.append(
            dict(
                state=str(rng.choice(STATES)),
                dependents=int(rng.choice([0, 0, 0, 1, 2])),
                members=[person()] + ([person()] if married else []),
            )
        )
    return out


HOUSEHOLDS = _households()


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
                    record = {
                        k: record[k]
                        for k in (
                            "social_security",
                            "employment_income",
                            "interest_income",
                            "dividend_income",
                        )
                    }
                people[name] = {
                    "age": {YEAR: 70},
                    **{k: {YEAR: val} for k, val in record.items()},
                }
                names.append(name)
                rows.append((i, v, j, name))
            spouses = list(names)
            dependents = []
            for k in range(h["dependents"]):
                name = f"{v}_{i}_d{k}"
                people[name] = {
                    "age": {YEAR: 10},
                    "is_tax_unit_dependent": {YEAR: True},
                }
                marital_units[f"mu_{name}"] = {"members": [name]}
                dependents.append(name)
            marital_units[f"mu_{v}_{i}"] = {"members": spouses}
            members = spouses + dependents
            tax_units[f"tu_{v}_{i}"] = {"members": members}
            spm_units[f"spm_{v}_{i}"] = {"members": members}
            units[f"hh_{v}_{i}"] = {
                "members": members,
                "state_code": {YEAR: h["state"]},
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


def _restated_countable(members):
    earned = sum(m["employment_income"] for m in members) / 12
    unearned = sum(m["social_security"] for m in members) / 12
    general = min(20, unearned)
    countable_unearned = unearned - general
    countable_earned = max(earned - 65 - (20 - general), 0) / 2
    return 12 * (countable_unearned + countable_earned)


def _fpg(state, size):
    fpg = P.gov.hhs.fpg(f"{YEAR}-01-01")
    group = state if state in ("AK", "HI", "PR") else "CONTIGUOUS_US"
    return fpg.first_person[group] + fpg.additional_person[group] * (size - 1)


def _value(values, index, variable, name):
    return values[variable][index[name]]


def test_countable_income_matches_restated_rule(sample):
    rows, index, values = sample
    for i, v, _, name in rows:
        members = [
            _variant(m, v, j == 0) for j, m in enumerate(HOUSEHOLDS[i]["members"])
        ]
        expected = _restated_countable(members)
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


def test_eligibility_and_benefit_match_restated_rules(sample):
    rows, index, values = sample
    amount = _per_recipient(YEAR)
    excluded = list(LIS.eligibility.ineligible_jurisdictions(f"{YEAR}-01-01"))
    limits = LIS.eligibility.resources(f"{YEAR}-01-01")
    for i, v, j, name in rows:
        h = HOUSEHOLDS[i]
        members = [_variant(m, v, k == 0) for k, m in enumerate(h["members"])]
        me = members[j]
        couple = len(members)
        size = couple + h["dependents"]
        assert _value(values, index, "part_d_lis_family_size", name) == size
        income_ok = _restated_countable(members) < 1.5 * _fpg(h["state"], size)
        resources = sum(m["bank_account_assets"] + m["stock_assets"] for m in members)
        limit = limits.limit.couple if couple == 2 else limits.limit.individual
        resource_ok = resources <= limit + limits.burial_exclusion * couple
        deemed = me["medicaid_enrolled"] or me["ssi"] > 0 or me["msp_eligible"]
        eligible = (
            me["medicare_enrolled"]
            and h["state"] not in excluded
            and (deemed or (income_ok and resource_ok))
        )
        automatic = me["medicaid_enrolled"] or me["ssi"] > 0
        enrolled = eligible and (automatic or me["takes_up_part_d_lis_if_eligible"])
        assert _value(values, index, "part_d_lis_income_eligible", name) == income_ok
        assert _value(values, index, "part_d_lis_resource_eligible", name) == (
            resource_ok
        )
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


def test_countable_income_matches_msp_countable_income():
    # No interest or dividends, everyone 70 and so Medicare eligible: the
    # MSP formula then counts the same income the same way, through its
    # couple branch for married couples and its personal branch otherwise.
    households = [
        {
            **h,
            "members": [
                {**m, "interest_income": 0, "dividend_income": 0} for m in h["members"]
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
