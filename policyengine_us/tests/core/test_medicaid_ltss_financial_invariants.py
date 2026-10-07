"""Property checks for the opt-in Medicaid LTSS financial-threshold screen.

The screen's YAML tests pin boundaries for hand-built households. These tests
check properties that must hold for every input, over a seeded random
population evaluated in one vectorized simulation, and check that the derived
limits agree with the parameters they are derived from.
"""

import numpy as np
import pytest

from policyengine_us import Simulation
from policyengine_us.system import system

PERIOD = "2026-07"
YEAR = "2026"
STATES = ["TX", "DE", "WA", "CA"]
PEOPLE_PER_STATE = 120
SEED = 9184

FINANCIAL = system.parameters.gov.hhs.medicaid.eligibility.long_term_care.financial
HOME_EQUITY = system.parameters.gov.hhs.medicaid.eligibility.long_term_care.home_equity
SSI = system.parameters.gov.ssa.ssi
CPI_U = system.parameters.gov.bls.cpi.cpi_u

OUTPUTS = [
    "medicaid_ltss_financial_pathway",
    "medicaid_ltss_special_income_limit",
    "medicaid_ltss_assistance_unit_size",
    "medicaid_ltss_individual_countable_income",
    "medicaid_ltss_countable_income",
    "medicaid_ltss_countable_resources",
    "medicaid_ltss_csra",
    "is_medicaid_ltss_income_eligible",
    "medicaid_ltss_csra_resource_eligible",
    "medicaid_ltss_home_equity_eligible",
    "medicaid_ltss_mmmna",
    "is_medicaid_ltss_financial_threshold_eligible",
]


def _random_people(rng):
    people = []
    for state in STATES:
        for _ in range(PEOPLE_PER_STATE):
            setting = rng.choice(
                ["INSTITUTIONAL", "HCBS", "UNKNOWN"], p=[0.6, 0.3, 0.1]
            )
            waiver = rng.choice(
                ["NONE", "WA_COPES", "WA_NEW_FREEDOM", "WA_RSW", "UNKNOWN"],
                p=[0.5, 0.15, 0.1, 0.1, 0.15],
            )
            market_value = float(rng.choice([0, rng.uniform(0, 2_500_000)]))
            people.append(
                dict(
                    state=state,
                    setting=str(setting),
                    waiver=str(waiver),
                    aged_blind_disabled=bool(rng.random() < 0.9),
                    unit_size=int(rng.choice([0, 1, 1, 1, 2, 3])),
                    earned_income=float(rng.uniform(0, 8_000)),
                    unearned_income=float(rng.uniform(0, 8_000)),
                    earned_qit=float(rng.choice([0, rng.uniform(0, 2_000)])),
                    unearned_qit=float(rng.choice([0, rng.uniform(0, 2_000)])),
                    needs_based_qit=float(rng.choice([0, rng.uniform(0, 100)])),
                    needs_based_income=float(rng.choice([0, rng.uniform(0, 500)])),
                    medically_needy_expenses=float(rng.uniform(0, 2_000)),
                    cost_of_care=float(rng.uniform(0, 12_000)),
                    resources=float(rng.uniform(0, 6_000)),
                    has_community_spouse=bool(rng.random() < 0.4),
                    snapshot=float(rng.uniform(0, 500_000)),
                    spouse_resources=float(rng.uniform(0, 250_000)),
                    initial_determination=bool(rng.random() < 0.5),
                    wa_start_year=int(rng.choice([1989, 1995, 2003, 2026, 0, 2027])),
                    wa_start_month=int(rng.choice([0, 1, 7, 8, 9, 10, 13])),
                    wa_sole_resources=float(rng.uniform(0, 6_000)),
                    wa_joint_resources=float(rng.uniform(0, 6_000)),
                    shelter=float(rng.uniform(0, 5_000)),
                    market_value=market_value,
                    encumbrances=float(rng.uniform(0, 1.2) * market_value),
                    ownership_share=float(
                        rng.choice([0, 0.5, 1, rng.uniform(-0.5, 1.5)])
                    ),
                    spouse_in_home=bool(rng.random() < 0.1),
                    child_under_21=bool(rng.random() < 0.05),
                    disabled_child=bool(rng.random() < 0.05),
                    hardship=bool(rng.random() < 0.05),
                )
            )
    # Ensure the ownership property covers both determination phases rather
    # than allowing chance to omit one phase in the small legacy cohort.
    legacy = [
        person
        for person in people
        if person["state"] == "WA"
        and person["has_community_spouse"]
        and 1 <= person["wa_start_month"] <= 12
        and 1 <= person["wa_start_year"]
        and person["wa_start_year"] * 100 + person["wa_start_month"] < 198910
    ]
    for index, person in enumerate(legacy):
        person["initial_determination"] = bool(index % 2)
    return people


def month(value):
    return {PERIOD: value}


def _situation(people, **overrides):
    situation = {"people": {}, "households": {}, "marital_units": {}}
    community_spouses = []
    for state in STATES:
        situation["households"][state] = {
            "members": [],
            "state_code": {YEAR: state},
        }
    for index, person in enumerate(people):
        person = {**person, **{k: v[index] for k, v in overrides.items()}}
        name = f"person_{index}"
        # Independent applicants have no couple-service facts. Delaware's
        # actual community spouses carry their own resource inventories.
        situation["marital_units"][name] = {"members": [name]}
        situation["households"][person["state"]]["members"].append(name)
        snapshot_variable = (
            "wa_medicaid_ltss_couple_countable_resources_at_most_recent_institutionalization"
            if person["state"] == "WA"
            else "medicaid_ltss_couple_countable_resources_at_first_institutionalization"
        )
        values = {
            "is_ssi_aged_blind_disabled": {YEAR: person["aged_blind_disabled"]},
            "medicaid_ltss_setting": month(person["setting"]),
            "medicaid_ltss_waiver": month(person["waiver"]),
            "medicaid_ltss_reported_gross_earned_income": month(
                person["earned_income"]
            ),
            "medicaid_ltss_reported_gross_unearned_income": month(
                person["unearned_income"]
            ),
            "medicaid_ltss_earned_income_deposited_to_qit": month(person["earned_qit"]),
            "medicaid_ltss_unearned_income_deposited_to_qit": month(
                person["unearned_qit"]
            ),
            "medicaid_ltss_needs_based_income": month(person["needs_based_income"]),
            "medicaid_ltss_needs_based_income_deposited_to_qit": month(
                person["needs_based_qit"]
            ),
            "medicaid_ltss_medically_needy_expenses": month(
                person["medically_needy_expenses"]
            ),
            "medicaid_ltss_cost_of_care": month(person["cost_of_care"]),
            "medicaid_ltss_has_community_spouse": month(person["has_community_spouse"]),
            "medicaid_ltss_is_initial_eligibility_determination": month(
                person["initial_determination"]
            ),
            snapshot_variable: month(person["snapshot"]),
            "medicaid_ltss_community_spouse_shelter_expenses": month(person["shelter"]),
            "medicaid_ltss_home_market_value": month(person["market_value"]),
            "medicaid_ltss_home_encumbrances": month(person["encumbrances"]),
            "medicaid_ltss_home_ownership_share": month(person["ownership_share"]),
            "medicaid_ltss_home_occupied_by_spouse": month(person["spouse_in_home"]),
            "medicaid_ltss_home_occupied_by_child_under_21": month(
                person["child_under_21"]
            ),
            "medicaid_ltss_home_occupied_by_blind_or_disabled_child": month(
                person["disabled_child"]
            ),
            "medicaid_ltss_home_equity_hardship_waiver": month(person["hardship"]),
        }
        if person["state"] == "DE":
            values["medicaid_ltss_individual_countable_resources"] = month(
                person["resources"]
            )
            if person["has_community_spouse"]:
                spouse = f"community_spouse_{index}"
                situation["marital_units"][name]["members"].append(spouse)
                situation["households"]["DE"]["members"].append(spouse)
                community_spouses.append((spouse, person["spouse_resources"]))
        else:
            # Existing non-Delaware explicit unit guards are still exercised.
            values["medicaid_ltss_non_delaware_assistance_unit_size"] = month(
                person["unit_size"]
            )
            values["medicaid_ltss_individual_countable_resources"] = month(
                person["resources"]
            )
            values[
                "medicaid_ltss_non_delaware_community_spouse_countable_resources"
            ] = month(person["spouse_resources"])
        if person["state"] == "WA":
            values.update(
                {
                    "wa_medicaid_ltss_most_recent_institutionalization_start_year": month(
                        person["wa_start_year"]
                    ),
                    "wa_medicaid_ltss_most_recent_institutionalization_start_month": month(
                        person["wa_start_month"]
                    ),
                    "wa_medicaid_ltss_solely_owned_countable_resources": month(
                        person["wa_sole_resources"]
                    ),
                    "wa_medicaid_ltss_jointly_owned_countable_resources": month(
                        person["wa_joint_resources"]
                    ),
                }
            )
        situation["people"][name] = values
    # Append spouses after all original records so output slices retain the
    # original state/person order regardless of marital-unit membership.
    for name, resources in community_spouses:
        situation["people"][name] = {
            "medicaid_ltss_individual_countable_resources": month(resources),
        }
    return situation


def _calculate(people, **overrides):
    simulation = Simulation(situation=_situation(people, **overrides))
    results = {}
    for variable in OUTPUTS:
        values = simulation.calculate(variable, PERIOD)
        if variable == "medicaid_ltss_financial_pathway":
            values = np.asarray(values.decode_to_str())
        results[variable] = np.asarray(values)[: len(people)]
    return results


@pytest.fixture(scope="module")
def population():
    rng = np.random.default_rng(SEED)
    people = _random_people(rng)

    def column(key):
        return np.array([person[key] for person in people])

    base = _calculate(people)
    deltas = rng.uniform(0.01, 3_000, len(people))
    shifted = {
        "earned_income": _calculate(
            people, earned_income=column("earned_income") + deltas
        ),
        "unearned_income": _calculate(
            people, unearned_income=column("unearned_income") + deltas
        ),
        "resources": _calculate(people, resources=column("resources") + deltas),
        "spouse_resources": _calculate(
            people, spouse_resources=column("spouse_resources") + deltas
        ),
        "market_value": _calculate(
            people, market_value=column("market_value") + 100 * deltas
        ),
        "shelter": _calculate(people, shelter=column("shelter") + deltas),
    }
    return people, column, base, shifted


def test_population_exercises_every_branch(population):
    _, column, base, _ = population
    pathway = base["medicaid_ltss_financial_pathway"]
    assert {"SPECIAL_INCOME", "INSTITUTIONAL_MEDICALLY_NEEDY", "UNMODELED"} <= set(
        pathway
    )
    composite = base["is_medicaid_ltss_financial_threshold_eligible"]
    assert composite.any() and not composite.all()
    assert (column("has_community_spouse") & (pathway != "UNMODELED")).any()


def test_composite_is_the_conjunction_of_the_screens(population):
    _, _, base, _ = population
    expected = (
        (base["medicaid_ltss_financial_pathway"] != "UNMODELED")
        & base["is_medicaid_ltss_income_eligible"]
        & base["medicaid_ltss_csra_resource_eligible"]
        & base["medicaid_ltss_home_equity_eligible"]
    )
    np.testing.assert_array_equal(
        base["is_medicaid_ltss_financial_threshold_eligible"], expected
    )


def test_unmodeled_pathway_fails_closed(population):
    _, column, base, _ = population
    unmodeled = base["medicaid_ltss_financial_pathway"] == "UNMODELED"
    assert unmodeled.any()
    for variable in [
        "is_medicaid_ltss_income_eligible",
        "medicaid_ltss_csra_resource_eligible",
        "is_medicaid_ltss_financial_threshold_eligible",
    ]:
        assert not base[variable][unmodeled].any(), variable
    assert (base["medicaid_ltss_mmmna"][unmodeled] == 0).all()
    assert (
        base["medicaid_ltss_financial_pathway"][column("state") == "CA"] == "UNMODELED"
    ).all()


def test_mmmna_stays_within_federal_bounds(population):
    _, column, base, _ = population
    mmmna = base["medicaid_ltss_mmmna"]
    minimum = FINANCIAL.federal.mmmna.minimum(f"{PERIOD}-01")
    maximum = FINANCIAL.federal.mmmna.maximum(f"{PERIOD}-01")
    receives = (base["medicaid_ltss_financial_pathway"] != "UNMODELED") & column(
        "has_community_spouse"
    )
    assert ((mmmna == 0) == ~receives).all()
    assert (mmmna[receives] >= minimum - 1e-9).all()
    assert (mmmna[receives] <= maximum + 1e-9).all()
    assert (mmmna[receives & (column("state") == "TX")] == maximum).all()


def test_home_equity_floor_and_exceptions_always_pass(population):
    _, column, base, _ = population
    eligible = base["medicaid_ltss_home_equity_eligible"]
    exception = (
        column("spouse_in_home")
        | column("child_under_21")
        | column("disabled_child")
        | column("hardship")
    )
    assert eligible[exception].all()
    share = column("ownership_share")
    equity = np.maximum(column("market_value") - column("encumbrances"), 0) * share
    floor = HOME_EQUITY.minimum_limit(f"{YEAR}-01-01")
    valid = (share >= 0) & (share <= 1)
    assert eligible[valid & (equity <= floor)].all()
    assert not eligible[~valid & ~exception].any()


@pytest.mark.parametrize(
    "shift, variable",
    [
        ("earned_income", "is_medicaid_ltss_income_eligible"),
        ("unearned_income", "is_medicaid_ltss_income_eligible"),
        ("resources", "medicaid_ltss_csra_resource_eligible"),
        ("spouse_resources", "medicaid_ltss_csra_resource_eligible"),
        ("market_value", "medicaid_ltss_home_equity_eligible"),
        ("earned_income", "is_medicaid_ltss_financial_threshold_eligible"),
        ("unearned_income", "is_medicaid_ltss_financial_threshold_eligible"),
        ("resources", "is_medicaid_ltss_financial_threshold_eligible"),
    ],
)
def test_screens_never_start_passing_when_a_countable_amount_rises(
    population, shift, variable
):
    _, _, base, shifted = population
    newly_passing = shifted[shift][variable] & ~base[variable]
    assert not newly_passing.any(), np.flatnonzero(newly_passing)[:5]


def _individual_countable_income(earned, unearned, needs, community_spouse):
    # Independent statutory sequence: spend the $20 general exclusion on
    # eligible unearned income first, then earnings; next $65, then half.
    general_from_unearned = min(max(unearned - needs, 0), 20)
    if community_spouse:
        return earned + unearned - min(max(earned + unearned - needs, 0), 20)
    remaining_general = 20 - general_from_unearned
    return (
        unearned - general_from_unearned + max(earned - remaining_general - 65, 0) / 2
    )


def test_raw_components_determine_income_in_the_statutory_order(population):
    people, _, base, shifted = population
    expected = []
    for person in people:
        earned = max(person["earned_income"] - person["earned_qit"], 0)
        unearned = max(person["unearned_income"] - person["unearned_qit"], 0)
        needs = min(person["needs_based_income"], person["unearned_income"])
        deposited_needs = min(
            person["needs_based_qit"],
            needs,
            person["unearned_qit"],
            person["unearned_income"],
        )
        needs = min(max(needs - deposited_needs, 0), unearned)
        expected.append(
            _individual_countable_income(
                earned, unearned, needs, person["has_community_spouse"]
            )
            if person["state"] == "DE"
            else earned + unearned
        )
    np.testing.assert_allclose(
        base["medicaid_ltss_individual_countable_income"],
        expected,
        rtol=1e-6,
        atol=0.001,
    )
    np.testing.assert_array_equal(
        base["medicaid_ltss_countable_income"],
        base["medicaid_ltss_individual_countable_income"],
    )
    for shift in ["earned_income", "unearned_income"]:
        assert (
            shifted[shift]["medicaid_ltss_countable_income"]
            >= base["medicaid_ltss_countable_income"] - 0.001
        ).all()


def test_delaware_independent_applicants_derive_individual_units(population):
    _, column, base, shifted = population
    delaware = column("state") == "DE"
    assert (base["medicaid_ltss_assistance_unit_size"][delaware] == 1).all()
    for results in shifted.values():
        np.testing.assert_array_equal(
            results["medicaid_ltss_assistance_unit_size"],
            base["medicaid_ltss_assistance_unit_size"],
        )
    np.testing.assert_allclose(
        base["medicaid_ltss_countable_resources"][delaware],
        column("resources")[delaware],
    )


def test_washington_dated_allocation_and_ownership_rules(population):
    _, column, base, _ = population
    washington = column("state") == "WA"
    has_spouse = column("has_community_spouse")
    onset = column("wa_start_year") * 100 + column("wa_start_month")
    valid = (
        (column("wa_start_year") >= 1)
        & (column("wa_start_month") >= 1)
        & (column("wa_start_month") <= 12)
        & (onset <= 202607)
    )
    pre_1989 = washington & (onset < 198910)
    legacy = washington & (onset >= 198910) & (onset < 200308)
    modern = washington & (onset >= 200308)
    maximum = FINANCIAL.federal.csra.maximum(f"{PERIOD}-01")
    floor = FINANCIAL.wa.csra.state_minimum(f"{PERIOD}-01")
    allowance = np.zeros(len(washington))
    allowance[legacy] = maximum
    allowance[modern] = np.minimum(
        np.maximum(column("snapshot")[modern] / 2, floor), maximum
    )
    mask = washington & has_spouse
    allowance[~valid | ~has_spouse] = 0
    np.testing.assert_allclose(
        base["medicaid_ltss_csra"][mask], allowance[mask], rtol=1e-6, atol=0.01
    )
    assert (pre_1989 & mask & valid & column("initial_determination")).any()
    assert (pre_1989 & mask & valid & ~column("initial_determination")).any()
    own_half = (column("wa_sole_resources") + column("wa_joint_resources")) / 2
    expected = (
        (base["medicaid_ltss_financial_pathway"] != "UNMODELED")
        & (base["medicaid_ltss_assistance_unit_size"] == 1)
        & valid
        & (own_half <= FINANCIAL.wa.resources.individual(f"{PERIOD}-01"))
    )
    mask = pre_1989 & has_spouse
    np.testing.assert_array_equal(
        base["medicaid_ltss_csra_resource_eligible"][mask], expected[mask]
    )
    assert not base["medicaid_ltss_csra_resource_eligible"][
        washington & has_spouse & ~valid
    ].any()


COUPLE_OUTPUTS = [
    "medicaid_ltss_individual_countable_income",
    "medicaid_ltss_couple_countable_income",
    "medicaid_ltss_assistance_unit_size",
    "medicaid_ltss_countable_income",
    "medicaid_ltss_countable_resources",
    "is_medicaid_ltss_income_eligible",
    "is_medicaid_ltss_financial_threshold_eligible",
]


def _random_couples():
    rng = np.random.default_rng(SEED + 1)
    couples = []
    for index in range(24):
        regime = index % 6
        couples.append(
            {
                "same_facility": regime < 4,
                "months": [0, 5, 6, 12, 0, 12][regime],
                "same_address_hcbs": regime == 4,
                "setting": "HCBS" if regime == 4 else "INSTITUTIONAL",
                "earned": rng.uniform(0, 6_000, 2),
                "unearned": rng.uniform(0, 1_500, 2),
                "resources": rng.uniform(0, 3_000, 2),
                "delta": float(rng.uniform(0.01, 3_000)),
            }
        )
        if regime == 2:
            # Random complementary inventories exercise favorable couple
            # elections exactly at six completed months, not just ties.
            couples[-1].update(
                {
                    "earned": np.array(
                        [rng.uniform(3_000, 4_000), rng.uniform(0, 500)]
                    ),
                    "unearned": rng.uniform(0, 200, 2),
                    "resources": np.array(
                        [rng.uniform(2_001, 2_900), rng.uniform(0, 100)]
                    ),
                }
            )
    return couples


def _couple_results(couples, raised_spouse=None, reverse=False):
    situation = {"people": {}, "households": {}, "marital_units": {}}
    for index, couple in enumerate(couples):
        names = [f"couple_{index}_a", f"couple_{index}_b"]
        situation["households"][f"couple_{index}"] = {
            "members": names,
            "state_code": {YEAR: "DE"},
        }
        situation["marital_units"][f"couple_{index}"] = {
            "members": list(reversed(names)) if reverse else names,
            "medicaid_ltss_spouses_requesting_or_receiving_institutional_services_in_same_facility": month(
                couple["same_facility"]
            ),
            "medicaid_ltss_spouses_months_in_same_institutional_facility": month(
                couple["months"]
            ),
            "medicaid_ltss_spouses_requesting_or_receiving_hcbs_at_same_address": month(
                couple["same_address_hcbs"]
            ),
        }
        for spouse, name in enumerate(names):
            situation["people"][name] = {
                "is_ssi_aged_blind_disabled": {YEAR: True},
                "medicaid_ltss_setting": month(couple["setting"]),
                "medicaid_ltss_reported_gross_earned_income": month(
                    float(couple["earned"][spouse])
                    + (couple["delta"] if spouse == raised_spouse else 0)
                ),
                "medicaid_ltss_reported_gross_unearned_income": month(
                    float(couple["unearned"][spouse])
                ),
                "medicaid_ltss_individual_countable_resources": month(
                    float(couple["resources"][spouse])
                ),
            }
    if reverse:
        situation["people"] = dict(reversed(list(situation["people"].items())))
    simulation = Simulation(situation=situation)
    results = {}
    for variable in reversed(COUPLE_OUTPUTS) if reverse else COUPLE_OUTPUTS:
        values = np.asarray(simulation.calculate(variable, PERIOD))
        # Compare by person identity after changing record and spouse order.
        results[variable] = values[::-1] if reverse else values
    return results


@pytest.fixture(scope="module")
def couples():
    people = _random_couples()
    return (
        people,
        _couple_results(people),
        [_couple_results(people, raised_spouse=spouse) for spouse in [0, 1]],
        _couple_results(people, reverse=True),
    )


def test_couple_budget_is_deterministic_under_role_and_calculation_order(couples):
    _, base, _, reversed_results = couples
    for variable in COUPLE_OUTPUTS:
        np.testing.assert_array_equal(
            base[variable], reversed_results[variable], err_msg=variable
        )
    units = base["medicaid_ltss_assistance_unit_size"].reshape(-1, 2)
    np.testing.assert_array_equal(units[:, 0], units[:, 1])


def test_derived_couple_budget_maximizes_the_number_of_eligible_spouses(couples):
    people, base, _, _ = couples
    instant = f"{PERIOD}-01"
    rate = FINANCIAL.de.special_income_limit.rate(instant)
    individual_limit = rate * SSI.amount.individual(instant)
    couple_limit = rate * SSI.amount.couple(instant)
    expected = []
    elected = []
    individual_incomes = []
    couple_incomes = []
    for couple in people:
        individual = [
            _individual_countable_income(earned, unearned, 0, False)
            for earned, unearned in zip(couple["earned"], couple["unearned"])
        ]
        combined = _individual_countable_income(
            sum(couple["earned"]), sum(couple["unearned"]), 0, False
        )
        individual_count = sum(
            income <= individual_limit and resources <= 2_000
            for income, resources in zip(individual, couple["resources"])
        )
        couple_count = 2 * (
            combined <= couple_limit and sum(couple["resources"]) <= 3_000
        )
        unit = 1
        if couple["same_address_hcbs"] or (
            couple["same_facility"] and couple["months"] < 6
        ):
            unit = 2
        elif couple["same_facility"]:
            unit = 2 if couple_count > individual_count else 1
            elected.append(unit)
        expected.extend([unit, unit])
        individual_incomes.extend(individual)
        couple_incomes.extend([combined, combined])
    # Both choices occur after month six, including ties favoring individuals.
    assert set(elected) == {1, 2}
    np.testing.assert_array_equal(base["medicaid_ltss_assistance_unit_size"], expected)
    np.testing.assert_allclose(
        base["medicaid_ltss_individual_countable_income"],
        individual_incomes,
        rtol=1e-6,
        atol=0.001,
    )
    np.testing.assert_allclose(
        base["medicaid_ltss_couple_countable_income"],
        couple_incomes,
        rtol=1e-6,
        atol=0.001,
    )
    expected_income = np.where(
        np.asarray(expected) == 2, couple_incomes, individual_incomes
    )
    np.testing.assert_allclose(
        base["medicaid_ltss_countable_income"], expected_income, rtol=1e-6, atol=0.001
    )


@pytest.mark.parametrize("raised_spouse", [0, 1])
@pytest.mark.parametrize(
    "variable",
    [
        "is_medicaid_ltss_income_eligible",
        "is_medicaid_ltss_financial_threshold_eligible",
    ],
)
def test_couple_screens_are_monotonic_in_either_spouses_raw_earnings(
    couples, raised_spouse, variable
):
    _, base, shifted, _ = couples
    newly_passing = shifted[raised_spouse][variable] & ~base[variable]
    assert not newly_passing.any(), np.flatnonzero(newly_passing)


def test_mmmna_is_non_decreasing_in_shelter_expenses(population):
    _, _, base, shifted = population
    assert (
        shifted["shelter"]["medicaid_ltss_mmmna"] >= base["medicaid_ltss_mmmna"] - 1e-9
    ).all()


def test_special_income_limit_matches_rate_times_ssi_federal_benefit_rate(
    population,
):
    _, column, base, _ = population
    individual = SSI.amount.individual(f"{PERIOD}-01")
    couple = SSI.amount.couple(f"{PERIOD}-01")
    instant = f"{PERIOD}-01"
    texas = FINANCIAL.tx.special_income_limit.rate(instant) * individual
    expected = {
        ("TX", 1): texas,
        ("TX", 2): texas * FINANCIAL.tx.special_income_limit.couple_multiplier(instant),
        ("DE", 1): FINANCIAL.de.special_income_limit.rate(instant) * individual,
        ("DE", 2): FINANCIAL.de.special_income_limit.rate(instant) * couple,
        ("WA", 1): FINANCIAL.wa.special_income_limit.rate(instant) * individual,
    }
    actual = base["medicaid_ltss_special_income_limit"]
    for index, (state, size) in enumerate(
        zip(column("state"), base["medicaid_ltss_assistance_unit_size"])
    ):
        assert actual[index] == pytest.approx(expected.get((state, size), 0))
    # The published 2026 figures (TX Appendix XXXI, DE A-14-2025, WA HCA).
    assert texas == 2_982
    assert expected[("DE", 2)] == 3_727.5


@pytest.mark.parametrize("year", [2027, 2030])
def test_special_income_limit_follows_the_uprated_federal_benefit_rate(year):
    period = f"{year}-01"
    simulation = Simulation(
        situation={
            "people": {
                "texas": {
                    "medicaid_ltss_non_delaware_assistance_unit_size": {period: 1}
                },
                "delaware": {"medicaid_ltss_setting": {period: "HCBS"}},
                "delaware_spouse": {"medicaid_ltss_setting": {period: "HCBS"}},
            },
            "households": {
                "texas_household": {
                    "members": ["texas"],
                    "state_code": {str(year): "TX"},
                },
                "delaware_household": {
                    "members": ["delaware", "delaware_spouse"],
                    "state_code": {str(year): "DE"},
                },
            },
            "marital_units": {
                "texas": {"members": ["texas"]},
                "delaware": {
                    "members": ["delaware", "delaware_spouse"],
                    "medicaid_ltss_spouses_requesting_or_receiving_hcbs_at_same_address": {
                        period: True
                    },
                },
            },
        }
    )
    instant = f"{period}-01"
    limits = simulation.calculate("medicaid_ltss_special_income_limit", period)
    assert limits[0] == pytest.approx(
        FINANCIAL.tx.special_income_limit.rate(instant) * SSI.amount.individual(instant)
    )
    assert limits[1] == pytest.approx(
        FINANCIAL.de.special_income_limit.rate(instant) * SSI.amount.couple(instant)
    )
    assert SSI.amount.individual(instant) > SSI.amount.individual("2026-01-01")


def test_minimum_home_equity_limit_indexes_like_cms():
    # 42 USC 1396p(f)(1)(C): September-to-September CPI-U, rounded to the
    # nearest $1,000, effective January 1. Applied to the 2025 value, the rule
    # reproduces CMS's published 2026 value.
    def indexed(value, year):
        change = CPI_U(f"{year - 1}-09-01") / CPI_U(f"{year - 2}-09-01")
        return round(value * change / 1_000) * 1_000

    assert indexed(HOME_EQUITY.minimum_limit("2025-01-01"), 2026) == 752_000
    for year in range(2027, 2036):
        prior = HOME_EQUITY.minimum_limit(f"{year - 1}-01-01")
        current = HOME_EQUITY.minimum_limit(f"{year}-01-01")
        assert current == indexed(prior, year)
        assert HOME_EQUITY.minimum_limit(f"{year}-12-01") == current


def test_indexed_minimum_home_equity_limit_is_capped_after_2028():
    years = [
        year
        for year in range(2028, 2100)
        if HOME_EQUITY.minimum_limit(f"{year}-01-01")
        > HOME_EQUITY.limit(f"{year}-01-01")
    ]
    assert years, "the indexed minimum never passes the $1,000,000 cap"
    year = years[0]
    cap = HOME_EQUITY.limit(f"{year}-01-01")
    assert cap == 1_000_000
    period = f"{year}-01"
    simulation = Simulation(
        situation={
            "people": {
                "at_cap": {
                    "medicaid_ltss_home_market_value": {period: cap},
                    "medicaid_ltss_home_ownership_share": {period: 1},
                },
                "above_cap": {
                    "medicaid_ltss_home_market_value": {period: cap + 1},
                    "medicaid_ltss_home_ownership_share": {period: 1},
                },
            },
            "households": {
                "household": {
                    "members": ["at_cap", "above_cap"],
                    "state_code": {str(year): "TX"},
                }
            },
        }
    )
    eligible = simulation.calculate("medicaid_ltss_home_equity_eligible", period)
    assert eligible.tolist() == [True, False]


def _income_exclusion_situation(state, values):
    """Independent applicants with actual monthly gross and source facts."""
    people = {}
    households = {}
    marital_units = {}
    for index, gross in enumerate(values):
        name = f"applicant_{index}"
        people[name] = {
            "age": {YEAR: 60},
            "meets_ssi_disability_criteria": {YEAR: True},
            "is_ssi_aged_blind_disabled": {YEAR: True},
            "medicaid_ltss_setting": month("INSTITUTIONAL"),
            "medicaid_ltss_non_delaware_assistance_unit_size": month(1),
            "medicaid_ltss_reported_gross_earned_income": month(float(gross[0])),
            "medicaid_ltss_reported_gross_unearned_income": month(float(gross[1])),
            "medicaid_ltss_impairment_related_work_expenses": month(400),
            "medicaid_ltss_reported_interest_income": month(100),
            "medicaid_ltss_reported_dividend_income": month(100),
            "medicaid_ltss_ssi_income": month(100),
            "medicaid_ltss_state_needs_based_public_assistance_income": month(100),
            "medicaid_ltss_qit_opening_year": month(2026),
            "medicaid_ltss_qit_opening_month": month(7),
            "medicaid_ltss_qit_subsequent_full_deposits_verified": month(True),
            "medicaid_ltss_qit_covered_earned_income": month(float(gross[0] / 2)),
            "medicaid_ltss_qit_covered_unearned_income": month(float(gross[1] / 2)),
            "medicaid_ltss_earned_income_deposited_to_qit": month(float(gross[0] / 8)),
            "medicaid_ltss_unearned_income_deposited_to_qit": month(
                float(gross[1] / 8)
            ),
            "medicaid_ltss_qit_covered_earned_income_deposited": month(
                float(gross[0] / 8)
            ),
            "medicaid_ltss_qit_covered_unearned_income_deposited": month(
                float(gross[1] / 8)
            ),
        }
        households[name] = {"members": [name], "state_code": {YEAR: state}}
        marital_units[name] = {"members": [name]}
    return {
        "people": people,
        "households": households,
        "marital_units": marital_units,
    }


@pytest.mark.parametrize("state", ["DE", "WA", "TX"])
def test_new_exclusions_keep_countable_income_between_zero_and_gross(state):
    rng = np.random.default_rng(SEED + 2)
    # Include zero and small incomes to exercise exclusion and deposit caps.
    gross = np.vstack(([0, 0], [1, 1], rng.uniform(0, 8_000, (96, 2))))
    simulation = Simulation(situation=_income_exclusion_situation(state, gross))
    income = simulation.calculate("medicaid_ltss_countable_income", PERIOD)
    assert (income >= 0).all()
    assert (income <= gross.sum(axis=1) + 0.001).all()
    for component, limit in [("earned", gross[:, 0]), ("unearned", gross[:, 1])]:
        remaining = simulation.calculate(
            f"medicaid_ltss_qit_adjusted_{component}_income", PERIOD
        )
        assert (remaining >= 0).all()
        assert (remaining <= limit + 0.001).all()


@pytest.mark.parametrize(
    "state, exclusion",
    [
        ("DE", "medicaid_ltss_impairment_related_work_expenses"),
        ("WA", "medicaid_ltss_reported_interest_income"),
        ("WA", "medicaid_ltss_reported_dividend_income"),
        ("WA", "medicaid_ltss_ssi_income"),
        ("WA", "medicaid_ltss_state_needs_based_public_assistance_income"),
        ("TX", "medicaid_ltss_qit_covered_earned_income"),
        ("TX", "medicaid_ltss_qit_covered_unearned_income"),
    ],
)
def test_each_new_exclusion_is_monotone(state, exclusion):
    rng = np.random.default_rng(SEED + 3)
    gross = rng.uniform(1, 8_000, (96, 2))
    situation = _income_exclusion_situation(state, gross)
    base = Simulation(situation=situation).calculate(
        "medicaid_ltss_countable_income", PERIOD
    )
    for person in situation["people"].values():
        person[exclusion][PERIOD] += 500
    changed = Simulation(situation=situation).calculate(
        "medicaid_ltss_countable_income", PERIOD
    )
    assert (changed <= base + 0.001).all()
    # Ensure the property covers effective deductions, not just a zero branch.
    assert (changed < base - 0.001).any()


@pytest.mark.parametrize("spouse", [0, 1])
def test_delaware_couple_work_expenses_share_exclusions_and_are_monotone(spouse):
    rng = np.random.default_rng(SEED + 4)
    gross = np.column_stack((rng.uniform(1_000, 6_000, 96), np.zeros(96)))
    situation = _income_exclusion_situation("DE", gross)
    # Isolate the work-expense ordering from trust deductions.
    for person in situation["people"].values():
        person["medicaid_ltss_earned_income_deposited_to_qit"] = month(0)
    situation["marital_units"] = {}
    for index in range(48):
        names = [f"applicant_{2 * index}", f"applicant_{2 * index + 1}"]
        situation["marital_units"][f"couple_{index}"] = {
            "members": names,
            "medicaid_ltss_spouses_requesting_or_receiving_institutional_services_in_same_facility": month(
                True
            ),
            "medicaid_ltss_spouses_months_in_same_institutional_facility": month(5),
        }
    base = Simulation(situation=situation).calculate(
        "medicaid_ltss_countable_income", PERIOD
    )
    combined_gross = gross[:, 0].reshape(-1, 2).sum(axis=1)
    expected = np.repeat((combined_gross - 20 - 65 - 800) / 2, 2)
    np.testing.assert_allclose(base, expected, rtol=1e-6, atol=0.001)
    assert (base <= np.repeat(combined_gross, 2) + 0.001).all()
    for index in range(48):
        situation["people"][f"applicant_{2 * index + spouse}"][
            "medicaid_ltss_impairment_related_work_expenses"
        ][PERIOD] += 500
    changed = Simulation(situation=situation).calculate(
        "medicaid_ltss_countable_income", PERIOD
    )
    assert (changed <= base + 0.001).all()
    np.testing.assert_allclose(changed, base - 250, rtol=1e-6, atol=0.001)


@pytest.mark.parametrize("source", ["earned", "unearned"])
def test_texas_whole_source_exclusion_applies_only_in_the_opening_month(source):
    people = {}
    observations = [(2026, month_number) for month_number in range(1, 13)]
    observations += [(2025, 7), (2027, 7)]
    for year, month_number in observations:
        period = f"{year}-{month_number:02}"
        people[f"month_{year}_{month_number}"] = {
            f"medicaid_ltss_reported_gross_{source}_income": {period: 4_000},
            f"medicaid_ltss_{source}_income_deposited_to_qit": {period: 500},
            "medicaid_ltss_qit_opening_year": {period: 2026},
            "medicaid_ltss_qit_opening_month": {period: 7},
            f"medicaid_ltss_qit_covered_{source}_income": {period: 4_000},
            f"medicaid_ltss_qit_covered_{source}_income_deposited": {period: 500},
            "medicaid_ltss_qit_subsequent_full_deposits_verified": {period: True},
        }
    names = list(people)
    simulation = Simulation(
        situation={
            "people": people,
            "households": {
                "household": {
                    "members": names,
                    "state_code": {str(year): "TX" for year in [2025, 2026, 2027]},
                }
            },
            "marital_units": {name: {"members": [name]} for name in names},
        }
    )
    for index, (year, month_number) in enumerate(observations):
        period = f"{year}-{month_number:02}"
        income = simulation.calculate(
            f"medicaid_ltss_qit_adjusted_{source}_income", period
        )[index]
        assert income == (0 if (year, month_number) == (2026, 7) else 3_500)
