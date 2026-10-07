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
                    income=float(rng.uniform(0, 8_000)),
                    needs_based_income=float(rng.choice([0, rng.uniform(0, 500)])),
                    medically_needy_expenses=float(rng.uniform(0, 2_000)),
                    cost_of_care=float(rng.uniform(0, 12_000)),
                    resources=float(rng.uniform(0, 6_000)),
                    has_community_spouse=bool(rng.random() < 0.4),
                    snapshot=float(rng.uniform(0, 500_000)),
                    spouse_resources=float(rng.uniform(0, 250_000)),
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
    return people


def month(value):
    return {PERIOD: value}


def _situation(people, **overrides):
    situation = {"people": {}, "households": {}, "marital_units": {}}
    for state in STATES:
        situation["households"][state] = {
            "members": [],
            "state_code": {YEAR: state},
        }
    for index, person in enumerate(people):
        person = {**person, **{k: v[index] for k, v in overrides.items()}}
        name = f"person_{index}"
        # Each random record is independent; the builder otherwise places
        # every person in one default marital unit.
        situation["marital_units"][name] = {"members": [name]}
        situation["households"][person["state"]]["members"].append(name)
        situation["people"][name] = {
            "is_ssi_aged_blind_disabled": {YEAR: person["aged_blind_disabled"]},
            "medicaid_ltss_setting": month(person["setting"]),
            "medicaid_ltss_waiver": month(person["waiver"]),
            "medicaid_ltss_assistance_unit_size": month(person["unit_size"]),
            "medicaid_ltss_qit_adjusted_income": month(person["income"]),
            "medicaid_ltss_income_disregards_already_applied": month(
                bool(person.get("disregards_applied", False))
            ),
            "medicaid_ltss_needs_based_income": month(person["needs_based_income"]),
            "medicaid_ltss_medically_needy_expenses": month(
                person["medically_needy_expenses"]
            ),
            "medicaid_ltss_cost_of_care": month(person["cost_of_care"]),
            "medicaid_ltss_countable_resources": month(person["resources"]),
            "medicaid_ltss_has_community_spouse": month(person["has_community_spouse"]),
            "medicaid_ltss_couple_countable_resources_at_first_institutionalization": month(
                person["snapshot"]
            ),
            "medicaid_ltss_community_spouse_countable_resources": month(
                person["spouse_resources"]
            ),
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
    # Households list members in state order, which matches `people` order.
    return situation


def _calculate(people, **overrides):
    simulation = Simulation(situation=_situation(people, **overrides))
    results = {}
    for variable in OUTPUTS:
        values = simulation.calculate(variable, PERIOD)
        if variable == "medicaid_ltss_financial_pathway":
            values = np.asarray(values.decode_to_str())
        results[variable] = np.asarray(values)
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
        "income": _calculate(people, income=column("income") + deltas),
        "resources": _calculate(people, resources=column("resources") + deltas),
        "spouse_resources": _calculate(
            people, spouse_resources=column("spouse_resources") + deltas
        ),
        "market_value": _calculate(
            people, market_value=column("market_value") + 100 * deltas
        ),
        "shelter": _calculate(people, shelter=column("shelter") + deltas),
        "disregards_applied": _calculate(
            people, disregards_applied=np.ones(len(people), dtype=bool)
        ),
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
        ("income", "is_medicaid_ltss_income_eligible"),
        ("resources", "medicaid_ltss_csra_resource_eligible"),
        ("spouse_resources", "medicaid_ltss_csra_resource_eligible"),
        ("market_value", "medicaid_ltss_home_equity_eligible"),
        ("income", "is_medicaid_ltss_financial_threshold_eligible"),
        ("resources", "is_medicaid_ltss_financial_threshold_eligible"),
    ],
)
def test_screens_never_start_passing_when_a_countable_amount_rises(
    population, shift, variable
):
    _, _, base, shifted = population
    newly_passing = shifted[shift][variable] & ~base[variable]
    assert not newly_passing.any(), np.flatnonzero(newly_passing)[:5]


def test_final_income_flag_only_removes_the_delaware_disregard(population):
    _, column, base, shifted = population
    final = shifted["disregards_applied"]
    delaware = column("state") == "DE"
    income_screens = [
        "is_medicaid_ltss_income_eligible",
        "is_medicaid_ltss_financial_threshold_eligible",
    ]
    for variable in OUTPUTS:
        if variable in income_screens:
            # Only Delaware applies a disregard, so the flag changes nothing
            # elsewhere, and skipping it can only make the screens harder.
            np.testing.assert_array_equal(
                final[variable][~delaware], base[variable][~delaware]
            )
            assert not (final[variable] & ~base[variable]).any(), variable
        else:
            np.testing.assert_array_equal(final[variable], base[variable])
    # With the flag, Delaware compares the supplied income itself.
    special = delaware & (base["medicaid_ltss_financial_pathway"] == "SPECIAL_INCOME")
    assert special.any()
    np.testing.assert_array_equal(
        final["is_medicaid_ltss_income_eligible"][special],
        column("income")[special]
        <= base["medicaid_ltss_special_income_limit"][special],
    )


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
    for index, (state, size) in enumerate(zip(column("state"), column("unit_size"))):
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
                "texas": {"medicaid_ltss_assistance_unit_size": {period: 1}},
                "delaware": {"medicaid_ltss_assistance_unit_size": {period: 2}},
            },
            "households": {
                "texas_household": {
                    "members": ["texas"],
                    "state_code": {str(year): "TX"},
                },
                "delaware_household": {
                    "members": ["delaware"],
                    "state_code": {str(year): "DE"},
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
