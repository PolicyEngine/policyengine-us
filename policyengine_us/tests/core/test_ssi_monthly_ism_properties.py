"""Check monthly SSI inputs, payment timing, and compatibility with main.

One Simulation holds randomized single adults plus couples and children who
share parental resources. Independent January 2026 SSI inputs check every
modeled state supplement outside the 2024 food change. Separate checks compare
all months and distinguish the income month from the payment month.

Python exercises the Simulation API's annual-to-monthly input conversion and
vectorized comparisons across periods and entities. YAML supplies individual
policy examples. This file runs in the existing Rest/core Python group.
"""

from types import SimpleNamespace

import numpy as np
import pytest
from hypothesis import example, given, settings
from hypothesis import strategies as st

from policyengine_core.periods import period as make_period
from policyengine_us import Simulation
from policyengine_us.system import system
from policyengine_us.variables.gov.ssa.ssi.eligibility.income.ism.ssi_in_kind_support_and_maintenance import (
    ssi_in_kind_support_and_maintenance,
)
from policyengine_us.variables.gov.ssa.ssi.eligibility.income.ism.ssi_pmv_amount import (
    ssi_pmv_amount,
)
from policyengine_us.variables.gov.ssa.ssi.eligibility.income.ism.ssi_pmv_applies import (
    ssi_pmv_applies,
)
from policyengine_us.variables.gov.ssa.ssi.eligibility.income.ssi_countable_income import (
    ssi_countable_income,
)
from policyengine_us.variables.gov.ssa.ssi.eligibility.status.ssi_federal_living_arrangement import (
    SSIFederalLivingArrangement,
)
from policyengine_us.variables.gov.ssa.ssi.ssi_amount_if_eligible import (
    ssi_amount_if_eligible,
)
from policyengine_us.variables.gov.ssa.ssi.ssi_if_takes_up import ssi_if_takes_up
from policyengine_us.variables.gov.ssa.ssi.uncapped_ssi import uncapped_ssi
from policyengine_us.variables.gov.ssa.ssi.uncapped_ssi_without_spousal_deeming import (
    uncapped_ssi_without_spousal_deeming,
)

YEARS = (2023, 2024, 2025)
STATES = ("CA", "CO", "FL", "IN", "KY", "LA", "MO", "MT", "NY", "OK")
SUPPLEMENTS = {
    "AK": "ak_ssp",
    "AL": "al_ssp",
    "CA": "ca_state_supplement",
    "CO": "co_state_supplement",
    "CT": "ct_ssp",
    "DC": "dc_ossp",
    "DE": "de_ssp",
    "FL": "fl_oss",
    "GA": "ga_ssp",
    "HI": "hi_oss",
    "IA": "ia_ssa",
    "ID": "id_aabd",
    "IL": "il_aabd",
    "IN": "in_ssp",
    "KS": "ks_sspp",
    "KY": "ky_ssp",
    "LA": "la_oss",
    "MA": "ma_state_supplement",
    "MD": "md_paa",
    "ME": "me_ssp",
    "MI": "mi_ssp",
    "MN": "mn_msa",
    "MO": "mo_ssp",
    "MT": "mt_ssp",
    "NC": "nc_sa",
    "NE": "ne_aabd",
    "NH": "nh_ssp",
    "NJ": "nj_ssp",
    "NM": "nm_ssi_state_supplement",
    "NV": "nv_oss",
    "NY": "ny_ssp",
    "OH": "oh_rss",
    "OK": "ok_ssp",
    "OR": "or_ssp",
    "PA": "pa_ssp",
    "RI": "ri_ssp",
    "SC": "sc_ssi_state_supplement",
    "SD": "sd_ssp",
    "TX": "tx_ssi_state_supplement",
    "UT": "ut_ssp",
    "VA": "va_ag",
    "VT": "vt_aabd",
    "WA": "wa_ssp",
    "WI": "wi_ssp",
    "WY": "wy_ssp",
}
N = 60


def _add_reference_households(situation):
    settings = {
        "AL": {"al_ssp_payment_category": "IHC_LEVEL_A", "al_ssp_eligible": True},
        "CO": {"age": 40, "is_disabled": True, "meets_ssi_disability_criteria": True},
        "FL": {"fl_oss_living_arrangement": "ALF", "fl_oss_eligible": True},
        "HI": {"hi_oss_living_arrangement": "COMMUNITY_CARE"},
        "IN": {"in_ssp_living_arrangement": "LICENSED_RESIDENTIAL"},
        "KY": {"ky_ssp_category": "PCH"},
        "LA": {
            "is_in_medicaid_facility": True,
            "ssi_lives_in_medical_treatment_facility": True,
            "ssi_medicaid_pays_majority_of_care": True,
            "social_security": 0,
        },
        "MD": {"md_paa_living_arrangement": "CARE_HOME_LEVEL_A"},
        "MO": {"mo_ssp_living_arrangement": "RCF_LEVEL_I"},
        "MT": {"mt_ssp_payment_category": "ASSISTED_LIVING_OR_GROUP_OR_COMMUNITY_HOME"},
        "NM": {"is_in_adult_residential_care": True},
        "TX": {
            "is_in_medicaid_facility": True,
            "ssi_lives_in_medical_treatment_facility": True,
            "ssi_medicaid_pays_majority_of_care": True,
            "social_security": 0,
        },
    }
    rows = {}
    for state in SUPPLEMENTS:
        kind = (
            "couple"
            if state in ("AK", "CA", "MA", "NJ")
            else "children"
            if state in ("NY", "OK")
            else "single"
        )
        roles = (
            ("parent", "child", "sibling")
            if kind == "children"
            else (("head", "spouse") if kind == "couple" else ("head",))
        )
        members = [f"reference_{state}_{role}" for role in roles]
        positions = []
        for i, (role, member) in enumerate(zip(roles, members)):
            child = role in ("child", "sibling")
            parent = role == "parent"
            values = {
                "age": 10 + i if child else 40 if parent else 70,
                "is_disabled": child,
                "meets_ssi_disability_criteria": child,
                "is_parent": parent,
                "is_tax_unit_head": i == 0,
                "is_tax_unit_spouse": role == "spouse",
                "is_tax_unit_dependent": child,
                "is_household_head": i == 0,
                "social_security": 0 if parent else 2_400 if child else 7_200,
                "ssi_countable_resources": 3_000 if parent else 0,
                **settings.get(state, {}),
            }
            positions.append(len(situation["people"]))
            situation["people"][member] = {
                name: {"2026": value} for name, value in values.items()
            }
        group_position = len(situation["spm_units"])
        for group in ("households", "tax_units", "families", "spm_units"):
            situation[group][f"reference_{state}"] = {"members": members}
        situation["households"][f"reference_{state}"]["state_code"] = {"2026": state}
        if kind == "children":
            for member in members:
                situation["marital_units"][member] = {"members": [member]}
        else:
            situation["marital_units"][f"reference_{state}"] = {"members": members}
        rows[state] = {"people": positions, "spm_unit": [group_position], "kind": kind}
    return rows


def _supplement_values(sim, rows):
    values = {}
    federal = sim.calculate("ssi", "2026-01")
    for state, name in SUPPLEMENTS.items():
        supplement = sim.calculate(name, "2026-01")
        entity = sim.tax_benefit_system.variables[name].entity.key
        indices = rows[state]["people" if entity == "person" else entity]
        values[state] = {
            "ssi": federal[rows[state]["people"]].tolist(),
            "supplement": supplement[indices].tolist(),
        }
    return values


def _independent_reference_values(sim, rows):
    """Check January 2026 against independent, constant monthly SSI inputs.

    Main e53b426082cd8953b30d8ede8b944f2d5f7246be defines countable income
    annually. The reference supplies annual FLOW inputs, so Core divides
    them across months. State formulas keep their native period reads.
    This reference covers these January 2026 households; it supplies no
    historical main output snapshot.
    """
    count = max(index for row in rows.values() for index in row["people"]) + 1
    countable, federal, deemed = (np.zeros(count) for _ in range(3))
    for state, row in rows.items():
        indices = row["people"]
        if row["kind"] == "couple":
            # (14,400 / 12 - 20) / 2 = 590 countable per spouse;
            # 1,491 / 2 - 590 = 155.50 federal SSI per spouse.
            countable[indices] = 590
            federal[indices] = 155.5
        elif row["kind"] == "children":
            # Each child counts 2,400 / 12 - 20 = 180 and receives
            # 994 - 180 = 814. The non-ABD parent receives no SSI.
            countable[indices[1:]] = 180
            federal[indices[1:]] = 814
            deemed[indices[1:]] = 500
        elif state in ("LA", "TX"):
            federal[indices] = 30
        else:
            # 7,200 / 12 - 20 = 580; federal SSI = 994 - 580 = 414.
            countable[indices] = 580
            federal[indices] = 414

    branch_name = "ssi_independent_monthly_reference"
    reference = sim.get_branch(branch_name)
    try:
        reference.set_input("ssi_countable_income", "2026", countable * 12)
        reference.set_input("ssi", "2026", federal * 12)
        reference.set_input(
            "ssi_in_kind_support_and_maintenance", "2026", np.zeros(count)
        )
        # Deemed resources use STOCK inputs; each month retains the $500
        # share of the parent's (3,000 - 2,000) / 2 excess.
        reference.set_input(
            "ssi_resources_deemed_from_ineligible_parent", "2026", deemed
        )
        return _supplement_values(reference, rows)
    finally:
        sim.branches.pop(branch_name, None)


def _households(seed=2024):
    rng = np.random.default_rng(seed)
    people, households, food_only, no_income = {}, {}, [], []
    for i in range(N):
        food = bool(rng.random() < 0.5)
        shelter = bool(rng.random() < 0.4)
        person = {
            "age": int(rng.choice([40, 66, 75])),
            "is_disabled": bool(rng.random() < 0.6),
            "employment_income": float(rng.choice([0, 0, 2_400, 9_600])),
            "social_security": float(rng.choice([0, 3_600, 7_200])),
            "ssi_receives_food_from_others": food,
            "ssi_receives_outside_shelter_support": shelter,
        }
        person["meets_ssi_disability_criteria"] = person["is_disabled"]
        if shelter and rng.random() < 0.3:
            person["ssi_shelter_support_value"] = float(rng.choice([1_200, 3_000]))
        people[f"p{i}"] = {
            k: {str(year): v for year in YEARS} for k, v in person.items()
        }
        households[f"h{i}"] = {
            "members": [f"p{i}"],
            "state_code": {str(year): STATES[i % len(STATES)] for year in YEARS},
        }
        food_only.append(food and not shelter)
        no_income.append(
            person["employment_income"] == 0 and person["social_security"] == 0
        )
    # Give each person their own unit of every group entity, as the
    # households are, so no income is shared between people.
    groups = {
        group: {f"{group}_{name}": {"members": [name]} for name in people}
        for group in ("tax_units", "spm_units", "families", "marital_units")
    }
    situation = {"people": people, "households": households, **groups}
    return situation, np.array(food_only), np.array(no_income)


@pytest.fixture(scope="module")
def results():
    situation, food_only, no_income = _households()
    reference_rows = _add_reference_households(situation)
    sim = Simulation(situation=situation)
    out = {}
    for year in YEARS:
        for month in range(1, 13):
            period = f"{year}-{month:02d}"
            values = {
                name: sim.calculate(name, period)
                for name in (
                    "ssi_countable_income",
                    "ssi_in_kind_support_and_maintenance",
                    "ssi_pmv_amount",
                    "ssi",
                    "is_ssi_eligible_individual",
                )
            }
            for state in STATES:
                name = SUPPLEMENTS[state]
                values[name] = sim.calculate(name, period)
            out[period] = values
        out[year] = sim.calculate("ssi_countable_income", year)
    # Build the reference before caching any January 2026 state payments.
    out["independent_2026"] = _independent_reference_values(sim, reference_rows)
    out["actual_2026"] = _supplement_values(sim, reference_rows)
    out["reference_rows"] = reference_rows
    for name in ("ssi_countable_income", "ssi_resources_deemed_from_ineligible_parent"):
        out[name] = sim.calculate(name, "2026-01")
    return out, food_only, no_income


def _assert_constant(values):
    np.testing.assert_allclose(
        values, np.broadcast_to(values[0], values.shape), atol=1e-6
    )


def _months(out, year, name, months=range(1, 13)):
    return np.stack([out[f"{year}-{m:02d}"][name] for m in months])[:, :N]


@pytest.mark.parametrize("year", [2023, 2025])
def test_months_match_when_nothing_changes_within_the_year(results, year):
    out, _, _ = results
    for name in ("ssi_countable_income", "ssi_in_kind_support_and_maintenance"):
        values = _months(out, year, name)
        _assert_constant(values)
    for name in ("ssi", *(SUPPLEMENTS[state] for state in STATES)):
        values = _months(out, year, name)
        _assert_constant(values)
    np.testing.assert_allclose(
        out[year][:N], 12 * _months(out, year, "ssi_countable_income")[0], rtol=1e-6
    )
    # ISM is capped by the PMV, a monthly amount (one-third of the federal
    # benefit rate plus $20, well under $600), not an annual one.
    ism = _months(out, year, "ssi_in_kind_support_and_maintenance")
    pmv = _months(out, year, "ssi_pmv_amount")
    assert np.all(ism <= pmv + 1e-6)
    assert np.all(pmv < 600)


def test_2024_food_income_changes_payments_from_december(results):
    out, food_only, _ = results
    before = range(1, 12)
    after = [12]
    for name in (
        "ssi_countable_income",
        "ssi",
        *(SUPPLEMENTS[state] for state in STATES),
    ):
        values = _months(out, 2024, name)
        others = values[:, ~food_only]
        _assert_constant(others)
        early = _months(out, 2024, name, before)[:, food_only]
        late = _months(out, 2024, name, after)[:, food_only]
        _assert_constant(early)
        _assert_constant(late)
    late_ism = _months(out, 2024, "ssi_in_kind_support_and_maintenance", after)
    assert not late_ism[:, food_only].any()
    ssi_nov = _months(out, 2024, "ssi", [11])[0]
    ssi_dec = _months(out, 2024, "ssi", [12])[0]
    assert np.all(ssi_dec >= ssi_nov - 1e-6)


def test_continuing_food_support_counts_eleven_income_months(results):
    out, food_only, no_income = results
    eligible = _months(out, 2024, "is_ssi_eligible_individual")[0].astype(bool)
    checked = food_only & no_income & eligible
    assert checked.any()
    # January-November payments use income months before the September 30
    # exclusion. ISM = 11 * (943 / 3 + 20) = 3,677.666667 annually.
    ism = _months(out, 2024, "ssi_in_kind_support_and_maintenance")[:, checked]
    np.testing.assert_allclose(ism.sum(axis=0), 11 * (943 / 3 + 20), atol=1e-3)
    np.testing.assert_allclose(ism[:11], 943 / 3 + 20, atol=1e-4)
    np.testing.assert_array_equal(ism[11], 0)
    # October and November pay 943 - 943 / 3 = 628.666667, rounded to
    # $628.67. December pays $943 after excluding October food income.
    for month, expected in ((10, 628.67), (11, 628.67), (12, 943)):
        np.testing.assert_allclose(
            _months(out, 2024, "ssi", [month])[0, checked], expected, atol=0.01
        )


@pytest.mark.parametrize("state", SUPPLEMENTS)
def test_ssi_and_each_supplement_match_independent_reference(results, state):
    out, _, _ = results
    for name in ("ssi", "supplement"):
        np.testing.assert_allclose(
            out["actual_2026"][state][name],
            out["independent_2026"][state][name],
            atol=1e-4,
            rtol=1e-6,
            err_msg=f"{state} {name} differs from independent SSI inputs",
        )


def test_reference_households_share_parental_resources_and_couple_income(results):
    out, _, _ = results
    for state in ("NY", "OK"):
        rows = out["reference_rows"][state]["people"]
        # A $3,000 parent resource pool exceeds the $2,000 allowance by
        # $1,000; each of two eligible children receives $500.
        np.testing.assert_allclose(
            out["ssi_resources_deemed_from_ineligible_parent"][rows], [0, 500, 500]
        )
    for state in ("AK", "CA", "MA", "NJ"):
        rows = out["reference_rows"][state]["people"]
        # The couple receives $14,400 / 12 = $1,200 monthly unearned
        # income. After the $20 exclusion, each spouse counts $590.
        np.testing.assert_allclose(out["ssi_countable_income"][rows], [590, 590])


@pytest.mark.parametrize(
    "payment_month,income_month",
    [
        ("2024-01", "2023-11"),
        ("2024-02", "2023-12"),
        ("2025-01", "2024-11"),
        ("2025-02", "2024-12"),
    ],
)
def test_payment_month_uses_second_prior_income_month(payment_month, income_month):
    assert str(make_period(payment_month).offset(-2, "month")) == income_month


@settings(max_examples=150, deadline=None, database=None, derandomize=True)
@given(
    year=st.sampled_from((2015, *YEARS)),
    month=st.integers(1, 12),
    food=st.booleans(),
    shelter=st.booleans(),
    late_food=st.booleans(),
)
@example(year=2015, month=1, food=True, shelter=False, late_food=False)
@example(year=2015, month=2, food=True, shelter=False, late_food=False)
@example(year=2024, month=1, food=True, shelter=False, late_food=False)
@example(year=2024, month=2, food=True, shelter=False, late_food=False)
@example(year=2025, month=1, food=True, shelter=False, late_food=False)
@example(year=2025, month=2, food=True, shelter=False, late_food=False)
@example(year=2024, month=11, food=True, shelter=False, late_food=True)
def test_pmv_reads_income_month_food_and_payment_month_shelter(
    year, month, food, shelter, late_food
):
    payment = make_period(f"{year}-{month:02d}")
    income_year = year - (month <= 2)
    income_month = (month - 3) % 12 + 1
    income = make_period(f"{income_year}-{income_month:02d}")
    support = income if income_year == year else payment
    person_reads, parameter_reads = {}, []

    def person(name, period):
        person_reads[name] = str(period)
        if name == "ssi_federal_living_arrangement":
            return SSIFederalLivingArrangement.OWN_HOUSEHOLD
        if name == "ssi_food_from_others_only_on_or_after_food_exclusion":
            value = late_food and str(period) == "2024-09"
        elif name == "ssi_receives_food_from_others":
            value = food if period == support else False
        else:
            values = {
                "ssi_receives_outside_shelter_support": shelter,
                "ssi_receives_shelter_from_others_in_household": False,
            }
            value = values[name] if period == payment else False
        return np.array([value])

    food_parameter = system.parameters.gov.ssa.ssi.income.ism.food_counts

    def read_food_counts(instant):
        parameter_reads.append(str(instant))
        return food_parameter(instant)

    # The formula reads food_counts as one parameter at each date, so the
    # fake tree is not callable: a parameters(date) call would fail here.
    parameters = SimpleNamespace(
        gov=SimpleNamespace(
            ssa=SimpleNamespace(
                ssi=SimpleNamespace(
                    income=SimpleNamespace(
                        ism=SimpleNamespace(food_counts=read_food_counts)
                    )
                )
            )
        )
    )

    actual = ssi_pmv_applies.formula(person, payment, parameters)
    counts_food = (year, month) < (2024, 12) and not (
        (year, month) == (2024, 11) and late_food
    )
    np.testing.assert_array_equal(actual, [shelter or (food and counts_food)])
    assert parameter_reads == [str(income.start), str(income.stop)]
    flag_month = person_reads.pop(
        "ssi_food_from_others_only_on_or_after_food_exclusion", None
    )
    # Only September 2024 income needs the day-specific food flag.
    # Other months must not cache irrelevant inputs before the model starts.
    assert flag_month == (str(income) if str(income) == "2024-09" else None)
    assert person_reads.pop("ssi_receives_food_from_others") == str(support)
    assert set(person_reads.values()) == {str(payment)}


@pytest.mark.parametrize("month", [1, 2, 10, 11, 12])
def test_couple_food_pmv_uses_payment_rate_and_splits_countable_income(month):
    payment = make_period(f"2024-{month:02d}")
    zero = np.zeros(3)
    values = {
        "ssi_couple_computation_applies": np.array([False, True, False]),
        "is_ssi_spousal_deeming_applies": np.array([False, False, True]),
        "ssi_federal_living_arrangement": SSIFederalLivingArrangement.OWN_HOUSEHOLD,
        "ssi_receives_food_from_others": np.ones(3, dtype=bool),
        "ssi_receives_outside_shelter_support": zero.astype(bool),
        "ssi_receives_shelter_from_others_in_household": zero.astype(bool),
        "ssi_food_from_others_only_on_or_after_food_exclusion": zero.astype(bool),
        "ssi_shelter_support_value": zero,
        "ssi_marital_earned_income": zero,
        "ssi_blind_or_disabled_working_student_exclusion": zero,
        "ssi_marital_unearned_income": zero,
        "ssi_earned_income": zero,
        "ssi_unearned_income": zero,
        "ssi_unearned_income_deemed_from_ineligible_parent": zero,
        "ssi_income_deemed_from_ineligible_spouse": zero,
        "is_ssi_aged_blind_disabled": np.ones(3, dtype=bool),
        "is_child": zero.astype(bool),
    }

    def person(name, period):
        return values[name]

    def parameters(period):
        instant = getattr(period, "start", period)
        return SimpleNamespace(
            gov=SimpleNamespace(
                ssa=SimpleNamespace(ssi=system.parameters.gov.ssa.ssi(instant))
            )
        )

    # ssi_pmv_applies reads food_counts as one parameter at each date.
    parameters.gov = system.parameters.gov

    formulas = (
        ("ssi_pmv_applies", ssi_pmv_applies),
        ("ssi_pmv_amount", ssi_pmv_amount),
        ("ssi_in_kind_support_and_maintenance", ssi_in_kind_support_and_maintenance),
        ("ssi_countable_income", ssi_countable_income),
        ("ssi_amount_if_eligible", ssi_amount_if_eligible),
        (
            "uncapped_ssi_without_spousal_deeming",
            uncapped_ssi_without_spousal_deeming,
        ),
        ("uncapped_ssi", uncapped_ssi),
        ("ssi_if_takes_up", ssi_if_takes_up),
    )
    for name, variable in formulas:
        values[name] = variable.formula(person, payment, parameters)

    # The 2024 joint PMV equals 1,415 / 3 + 20 = 491.666667.
    # Spousal deeming uses half that PMV: 245.833333. January and February
    # retain the payment month's rate while reading the prior year's food dates.
    np.testing.assert_allclose(
        values["ssi_pmv_amount"],
        [943 / 3 + 20, 1_415 / 3 + 20, (1_415 / 3 + 20) / 2],
    )
    # Through November each spouse counts (491.666667 - 20) / 2 =
    # 235.833333, then receives 1,415 / 2 - 235.833333 = 471.666667.
    # December excludes food, so each spouse receives 1,415 / 2 = 707.50.
    countable = 0 if month == 12 else 1_415 / 6
    assert values["ssi_countable_income"][1] == pytest.approx(countable)
    assert values["ssi_amount_if_eligible"][1] == pytest.approx(1_415 / 2)
    assert values["ssi_if_takes_up"][1] == pytest.approx(1_415 / 2 - countable)
    # Under deeming, 416.1163(e)(2) limits the payment to the individual rate
    # less the claimant's own income, with the individual PMV of 943 / 3 + 20
    # (POMS SI 01320.150 B.1.b): 943 - 943 / 3 = 628.666667 through November
    # and 943 once October income excludes food. The deeming computation
    # leaves 1,415 - 225.833333 through November and 1,415 in December, more
    # than that limit in each month.
    individual = 943 if month == 12 else 943 - 943 / 3
    assert values["uncapped_ssi_without_spousal_deeming"][2] == pytest.approx(
        individual
    )
    assert values["ssi_if_takes_up"][2] == pytest.approx(individual)


def test_annual_countable_income_input_reaches_each_month():
    # A separate simulation: an input sets the variable for every person.
    sim = Simulation(
        situation={
            "people": {
                "p": {"age": {"2025": 70}, "ssi_countable_income": {"2025": 6_000}}
            },
            "households": {"h": {"members": ["p"], "state_code": {"2025": "FL"}}},
        }
    )
    for month in range(1, 13):
        assert sim.calculate("ssi_countable_income", f"2025-{month:02d}")[
            0
        ] == pytest.approx(500)


@pytest.mark.parametrize("year", YEARS)
def test_month_countable_income_is_that_months_ism_without_other_income(results, year):
    # The $20 general exclusion applies first to unearned income, which ISM
    # is (20 CFR 416.1124, as _apply_ssi_exclusions_monthly applies it). With
    # no other income, each month's countable income is its ISM less $20.
    out, _, no_income = results
    ism = _months(out, year, "ssi_in_kind_support_and_maintenance")
    countable = _months(out, year, "ssi_countable_income")
    # Countable income is computed only for an eligible individual or spouse;
    # these units are single people.
    eligible = _months(out, year, "is_ssi_eligible_individual").astype(bool)
    checked = eligible & no_income
    assert (ism[checked] > 20).any()
    np.testing.assert_allclose(
        countable[checked], np.maximum(ism[checked] - 20, 0), atol=1e-4
    )
