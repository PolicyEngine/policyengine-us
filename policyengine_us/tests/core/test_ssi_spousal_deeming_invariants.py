"""Simulation-API invariants for SSI couples and spousal deeming.

Two vectorized grid simulations, each built once per module, plus small
simulations for the generated income and state-supplement properties:

- An income grid of 400 two-person households: an aged claimant with only
  unearned income and a spouse under 65 with unearned and earned income. The
  axes include the $20 and $65 exclusion edges, the $497 deeming threshold
  ($1,491 couple less $994 individual Federal benefit rate in 2026) and its
  neighbours, and a claimant income that leaves nothing of the individual
  rate. SSI must equal an independent numpy reading of 20 CFR 416.1163, never
  exceed the benefit without deeming (416.1163(e)(2)), and never rise when any
  income rises.
- A role grid of 72 three-adult households: a married couple living with a
  third adult, over all nine assignments of tax-unit head and spouse roles
  among the three adults and aged or not for each adult, plus two-person and
  one-person households in the same simulation. Couple status and SSI must
  not depend on tax roles or on the third adult (416.1801(c), 416.1806,
  416.1160(d)), and joint claims must be symmetric and disjoint from
  ineligible-spouse status.
- Every implemented state supplement, comparing a couple and third adult
  with the API's default marital unit against explicit couple/single units.
  Hypothesis varies income, age, resources and care membership; explicit
  examples retain the payment, exclusion, eligibility and resource edges.
  Each comparison uses two independent three-person simulations sharing the
  same read-only system as the grids.
- Declared spouses who live in separate households in Colorado, Missouri,
  Oregon, South Dakota, Virginia and Iowa, comparing their supplements before and
  after an unrelated adult joins either household. The marriage, separate
  tax/family/SPM budgets, and all benefit inputs stay the same. Six explicit
  examples and two generated examples use two small independent simulations
  apiece per state, sharing the same read-only system. Generated examples
  enter the states' care budgets; independent budget checks also detect a
  lost spouse when both simulations make the same error.
- Separated parent/child and dependent pairs in the retained-marriage state
  programs, comparing the default marital unit with explicit singletons.
  Generated incomes and resources exercise both relationship exclusions.

YAML covers worked cases. Python is needed to check the for-all properties
over every ordered edge of the grids and to compare with an oracle that does
not use the model. Both grids share the read-only system singleton; neither
constructs a model per household. This file routes to the Rest/core group.
"""

from copy import deepcopy
from itertools import product
from pathlib import Path

import numpy as np
import pytest
import yaml
from hypothesis import HealthCheck, example, given, settings
from hypothesis import strategies as st
from policyengine_core.periods import period as make_period

from policyengine_us import Simulation
from policyengine_us.variables.gov.states._spouses import (
    state_couple_total,
    state_is_married,
)

YEAR = 2026
PERIOD = "2026-01"
INDIVIDUAL_FBR = 994
COUPLE_FBR = 1_491
GENERAL_EXCLUSION = 20
EARNED_EXCLUSION = 65

CLAIMANT_UNEARNED = (0, 19, 20, 400, 743, 974, 1_014, 1_200)
SPOUSE_UNEARNED = (0, 100, 300, 497, 498)
SPOUSE_EARNED = (0, 64, 65, 400, 496, 497, 498, 600, 1_000, 3_100)


def _countable(unearned, earned):
    """416.1112, 416.1124: $20 general, then $65 and half of the rest."""
    general = np.minimum(GENERAL_EXCLUSION, unearned)
    leftover = GENERAL_EXCLUSION - general
    earned_after = np.maximum(earned - EARNED_EXCLUSION - leftover, 0) / 2
    return unearned - general + earned_after


def _oracle_ssi(claimant_unearned, spouse_unearned, spouse_earned, claimant_earned=0):
    """Monthly SSI for an aged claimant with an ineligible spouse.

    416.1163(d)(1): no deeming when the spouse's income is not more than the
    couple rate less the individual rate. (d)(2): otherwise the couple's
    combined countable income is subtracted from the couple rate. (e)(2): the
    benefit is the lesser of that and the individual rate less the claimant's
    own countable income.
    """
    alone = np.maximum(
        INDIVIDUAL_FBR - _countable(claimant_unearned, claimant_earned),
        0,
    )
    couple = np.maximum(
        COUPLE_FBR
        - _countable(
            claimant_unearned + spouse_unearned, claimant_earned + spouse_earned
        ),
        0,
    )
    deems = spouse_unearned + spouse_earned > COUPLE_FBR - INDIVIDUAL_FBR
    return np.where(deems, np.minimum(couple, alone), alone)


def _income_situation(rows, claimant_earnings=None):
    situation = {
        plural: {}
        for plural in (
            "people",
            "tax_units",
            "households",
            "marital_units",
            "families",
            "spm_units",
        )
    }
    for index, (claimant_unearned, spouse_unearned, spouse_earned) in enumerate(rows):
        claimant, spouse = f"c{index}", f"s{index}"
        situation["people"][claimant] = {
            "age": {YEAR: 70},
            "pension_income": {YEAR: 12 * claimant_unearned},
            "employment_income": {
                YEAR: 12 * claimant_earnings[index] if claimant_earnings else 0
            },
        }
        situation["people"][spouse] = {
            "age": {YEAR: 60},
            "pension_income": {YEAR: 12 * spouse_unearned},
            "employment_income": {YEAR: 12 * spouse_earned},
        }
        members = [claimant, spouse]
        for plural in (
            "tax_units",
            "households",
            "marital_units",
            "families",
            "spm_units",
        ):
            situation[plural][f"u{index}"] = {"members": members}
        situation["households"][f"u{index}"]["state_code"] = {YEAR: "TX"}
    return situation


def _income_ssi(rows, claimant_earnings=None):
    simulation = Simulation(situation=_income_situation(rows, claimant_earnings))
    ssi = simulation.calculate("ssi", PERIOD)
    without_deeming = simulation.calculate(
        "uncapped_ssi_without_spousal_deeming", PERIOD
    )
    return ssi[0::2], ssi[1::2], np.maximum(without_deeming[0::2], 0)


@pytest.fixture(scope="module")
def income_grid():
    rows = list(product(CLAIMANT_UNEARNED, SPOUSE_UNEARNED, SPOUSE_EARNED))
    claimant_ssi, spouse_ssi, without_deeming = _income_ssi(rows)
    shape = (len(CLAIMANT_UNEARNED), len(SPOUSE_UNEARNED), len(SPOUSE_EARNED))
    columns = np.array(rows, dtype=float).T
    return {
        "rows": columns,
        "ssi": claimant_ssi.reshape(shape),
        "spouse_ssi": spouse_ssi,
        "without_deeming": without_deeming.reshape(shape),
        "oracle": _oracle_ssi(*columns).reshape(shape),
    }


def test_income_grid_matches_independent_oracle(income_grid):
    np.testing.assert_allclose(income_grid["ssi"], income_grid["oracle"], atol=0.01)
    assert np.all(income_grid["spouse_ssi"] == 0)


def test_deemed_benefit_never_exceeds_benefit_without_deeming(income_grid):
    assert np.all(income_grid["ssi"] <= income_grid["without_deeming"] + 0.01)


@pytest.mark.parametrize("axis", [0, 1, 2], ids=["claimant", "unearned", "earned"])
def test_ssi_never_rises_with_income(income_grid, axis):
    # Each axis is sorted ascending, so every ordered edge is a rise in one
    # income with the others fixed.
    assert np.all(np.diff(income_grid["ssi"], axis=axis) <= 0.01)


def test_claimant_wages_preserve_the_cap_with_and_without_deeming():
    """The two #10138 cases share the same individual countable-income cap."""
    spouse_earnings = (6_000, 5_900)
    situation = _income_situation(
        [(0, 0, income / 12) for income in spouse_earnings],
        claimant_earnings=(1_000, 1_000),
    )
    for index, income in enumerate(spouse_earnings):
        claimant = situation["people"][f"c{index}"]
        spouse = situation["people"][f"s{index}"]
        claimant["age"] = {YEAR: 67}
        spouse["age"] = {YEAR: 45}
        spouse.pop("employment_income")
        spouse["self_employment_income"] = {YEAR: income}
    simulation = Simulation(situation=situation)
    np.testing.assert_array_equal(
        simulation.calculate("is_ssi_spousal_deeming_applies", YEAR)[0::2],
        [True, False],
    )
    # $994 - ($1,000 - $20 - $65) / 2 = $536.50 monthly, $6,438 annually.
    np.testing.assert_allclose(
        simulation.calculate("ssi", YEAR)[0::2], [6_438, 6_438], atol=0.01
    )


@settings(
    max_examples=3,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow],
)
@given(
    st.lists(
        st.tuples(
            st.integers(0, 1_300),
            st.integers(0, 900),
            st.integers(0, 3_500),
            st.integers(0, 2_500),
        ),
        min_size=40,
        max_size=40,
    )
)
def test_random_incomes_match_independent_oracle(rows):
    # Add the three sides of the $497 threshold to the same simulation, so
    # generated claimant wages exercise 416.1163(e)(2) without more setup.
    income_rows = [row[:3] for row in rows]
    claimant_earnings = [row[3] for row in rows]
    for claimant_unearned, _, _, claimant_earned in rows:
        for spouse_unearned in (496, 497, 498):
            income_rows.append((claimant_unearned, spouse_unearned, 0))
            claimant_earnings.append(claimant_earned)
    claimant_ssi, _, _ = _income_ssi(income_rows, claimant_earnings)
    expected = _oracle_ssi(
        *np.array(income_rows, dtype=float).T, np.asarray(claimant_earnings)
    )
    np.testing.assert_allclose(claimant_ssi, expected, atol=0.01)
    threshold = claimant_ssi[len(rows) :].reshape(len(rows), 3)
    np.testing.assert_allclose(threshold[:, 0], threshold[:, 1], atol=0.01)
    # One extra dollar of spouse income may reduce SSI by at most a dollar;
    # starting deeming cannot cause a jump when the claimant earns wages.
    assert np.all(np.diff(threshold, axis=1) <= 0.01)
    assert np.all(np.diff(threshold, axis=1) >= -1.01)


# Role grid: adults "a" and "b" are married; "c" lives with them in its own
# marital unit. Every head/spouse assignment among the three is supplied.
# The same simulation also holds two-person and one-person households, so
# household positions differ across rows.
ADULTS = ("a", "b", "c")
ROLE_ASSIGNMENTS = [
    (head, spouse) for head in ADULTS for spouse in (None, *ADULTS) if spouse != head
]
AGED = (False, True)
INCOME = {"a": 600, "b": 300, "c": 900}


def _adult(age, income, head=False, spouse=False):
    return {
        "age": {YEAR: age},
        "pension_income": {YEAR: 12 * income},
        "is_tax_unit_head": {YEAR: head},
        "is_tax_unit_spouse": {YEAR: spouse},
    }


def _role_situation():
    situation = {
        plural: {}
        for plural in (
            "people",
            "tax_units",
            "households",
            "marital_units",
            "families",
            "spm_units",
        )
    }

    def add_household(key, people, marital_units):
        situation["people"].update(people)
        for plural in ("tax_units", "households", "families", "spm_units"):
            situation[plural][key] = {"members": list(people)}
        situation["households"][key]["state_code"] = {YEAR: "TX"}
        for index, members in enumerate(marital_units):
            situation["marital_units"][f"{key}_m{index}"] = {"members": members}

    configurations = list(product(product(AGED, repeat=3), ROLE_ASSIGNMENTS))
    for index, (aged, (head, spouse)) in enumerate(configurations):
        names = {adult: f"{adult}{index}" for adult in ADULTS}
        people = {
            names[adult]: _adult(
                70 if is_aged else 50,
                INCOME[adult],
                head=adult == head,
                spouse=adult == spouse,
            )
            for adult, is_aged in zip(ADULTS, aged)
        }
        add_household(f"u{index}", people, [[names["a"], names["b"]], [names["c"]]])
    extras = list(product(AGED, repeat=2))
    for index, (a_aged, b_aged) in enumerate(extras):
        couple = {
            f"pa{index}": _adult(70 if a_aged else 50, INCOME["a"], head=True),
            f"pb{index}": _adult(70 if b_aged else 50, INCOME["b"], spouse=True),
        }
        add_household(f"pair{index}", couple, [list(couple)])
        single = {f"s{index}": _adult(70 if a_aged else 50, INCOME["c"], head=True)}
        add_household(f"single{index}", single, [list(single)])
    return situation, configurations, extras


@pytest.fixture(scope="module")
def role_grid():
    situation, configurations, extras = _role_situation()
    simulation = Simulation(situation=situation)
    grid_people = 3 * len(configurations)
    shape = (len(configurations) // len(ROLE_ASSIGNMENTS), len(ROLE_ASSIGNMENTS), 3)

    def calculate(variable, period):
        values = simulation.calculate(variable, period)
        return values[:grid_people].reshape(shape), values[grid_people:].reshape(
            len(extras), 3
        )

    joint, joint_extra = calculate("ssi_claim_is_joint", YEAR)
    ineligible, ineligible_extra = calculate("is_ssi_ineligible_spouse", YEAR)
    ssi, ssi_extra = calculate("ssi", PERIOD)
    return {
        "aged": [aged for aged, _ in configurations[:: len(ROLE_ASSIGNMENTS)]],
        "joint": joint,
        "ineligible_spouse": ineligible,
        "ssi": ssi,
        "extras": extras,
        "joint_extra": joint_extra,
        "ineligible_extra": ineligible_extra,
        "ssi_extra": ssi_extra,
    }


def test_couple_status_and_ssi_do_not_depend_on_tax_roles(role_grid):
    for name in ("joint", "ineligible_spouse", "ssi"):
        values = role_grid[name]
        assert np.all(values == values[:, :1, :]), name


def test_couple_status_matches_the_couple_definitions(role_grid):
    # 416.1801(c) and 416.1160(d), with aged, blind or disabled status
    # standing for SSI eligibility (ssi_claim_is_joint does not apply the
    # citizenship condition).
    for index, aged in enumerate(role_grid["aged"]):
        couple = aged[0] and aged[1]
        assert np.all(role_grid["joint"][index, :, :2] == couple)
        # The third adult is not married to either spouse.
        assert not np.any(role_grid["joint"][index, :, 2])
        assert not np.any(role_grid["ineligible_spouse"][index, :, 2])
        ineligible = role_grid["ineligible_spouse"][index]
        assert np.all(ineligible[:, 0] == (aged[1] and not aged[0]))
        assert np.all(ineligible[:, 1] == (aged[0] and not aged[1]))
    assert not np.any(role_grid["joint"] & role_grid["ineligible_spouse"])


def test_role_grid_couples_match_the_same_couple_living_alone(role_grid):
    # Columns are (pair a, pair b, single). A couple's status and SSI do not
    # change when a third adult shares their household and tax unit.
    joint_extra = role_grid["joint_extra"]
    ssi_extra = role_grid["ssi_extra"]
    for index, (a_aged, b_aged) in enumerate(role_grid["extras"]):
        assert np.all(joint_extra[index, :2] == (a_aged and b_aged))
        assert not joint_extra[index, 2]
        assert not role_grid["ineligible_extra"][index, 2]
        rows = [
            row
            for row, aged in enumerate(role_grid["aged"])
            if aged[:2] == (a_aged, b_aged)
        ]
        for row in rows:
            np.testing.assert_allclose(
                role_grid["ssi"][row, 0, :2], ssi_extra[index, :2], atol=0.01
            )


# Every implemented state supplement, including programs paid to an SPM unit
# rather than directly to a person. Annual programs are compared annually.
SUPPLEMENT_PROGRAMS = {
    "AK": ("ak_ssp",),
    "AL": ("al_ssp",),
    "CA": ("ca_state_supplement", "ca_capi"),
    "CO": ("co_state_supplement", "co_oap"),
    "CT": ("ct_ssp",),
    "DC": ("dc_ossp",),
    "DE": ("de_ssp",),
    "FL": ("fl_oss",),
    "GA": ("ga_ssp",),
    "HI": ("hi_oss",),
    "IA": ("ia_ssa",),
    "ID": ("id_aabd",),
    "IL": ("il_aabd",),
    "IN": ("in_ssp",),
    "KS": ("ks_sspp",),
    "KY": ("ky_ssp",),
    "LA": ("la_oss",),
    "MA": ("ma_state_supplement",),
    "MD": ("md_paa",),
    "ME": ("me_ssp",),
    "MI": ("mi_ssp",),
    "MN": ("mn_msa",),
    "MO": ("mo_ssp",),
    "MT": ("mt_ssp",),
    "NC": ("nc_sa",),
    "NE": ("ne_aabd",),
    "NH": ("nh_ssp",),
    "NJ": ("nj_ssp",),
    "NM": ("nm_ssi_state_supplement",),
    "NV": ("nv_oss",),
    "NY": ("ny_ssp",),
    "OH": ("oh_rss",),
    "OK": ("ok_ssp",),
    "OR": ("or_ssp",),
    "PA": ("pa_ssp",),
    "RI": ("ri_ssp",),
    "SC": ("sc_ssi_state_supplement",),
    "SD": ("sd_ssp",),
    "TX": ("tx_ssi_state_supplement",),
    "UT": ("ut_ssp",),
    "VA": ("va_ag",),
    "VT": ("vt_aabd",),
    "WA": ("wa_ssp",),
    "WI": ("wi_ssp",),
    "WY": ("wy_ssp",),
}


def test_state_supplement_inventory_matches_program_registry():
    """The property includes every implemented supplement in the registry."""
    registry_path = Path(__file__).resolve().parents[2] / "programs.yaml"
    registry = yaml.safe_load(registry_path.read_text())
    supplements = next(
        program
        for program in registry["programs"]
        if program["id"] == "ssi_state_supplement"
    )
    implemented = {
        entry["state"]: entry["variable"]
        for entry in supplements["state_implementations"]
        if entry.get("variable")
    }
    assert implemented.keys() == SUPPLEMENT_PROGRAMS.keys()
    for state, variable in implemented.items():
        assert variable in SUPPLEMENT_PROGRAMS[state], (state, variable)


# Conditions that exercise care-only supplements and CAPI. These are inputs,
# not substitute payment amounts or eligibility results. The builder reads
# each variable's entity and period: Delaware's arrangement belongs to the
# household, while most states' care settings belong to the person.
SUPPLEMENT_CARE_INPUTS = {
    "AL": {
        "al_receives_elderly_disabled_medicaid_waiver": True,
        "al_meets_snf_criteria": True,
        "al_ssp_care_setting": "PRIVATE_HOME_IHC",
    },
    "CA": {
        "immigration_status_str": "LEGAL_PERMANENT_RESIDENT",
        "ssi_qualifying_quarters_earnings": 0,
    },
    "DC": {"dc_ossp_in_adult_foster_care": True},
    "DE": {"de_ssp_living_arrangement": "CERTIFIED_RESIDENTIAL_CARE_HOME"},
    "FL": {"fl_oss_program_track": "REDESIGN", "fl_oss_community_care_type": "ALF"},
    "HI": {"hi_oss_care_facility_type": "COMMUNITY_CARE"},
    "IA": {"ia_ssa_category": "FAMILY_LIFE_HOME"},
    "ID": {"id_aabd_living_arrangement": "ROOM_AND_BOARD"},
    "IN": {
        "ssi_lives_in_medical_treatment_facility": True,
        "ssi_medicaid_pays_majority_of_care": True,
        "medicaid_enrolled": True,
    },
    "KS": {
        "ssi_lives_in_medical_treatment_facility": True,
        "ssi_medicaid_pays_majority_of_care": True,
    },
    "KY": {"ky_ssp_category": "CARETAKER", "ky_ssp_care_receivers": "BOTH"},
    "LA": {
        "ssi_lives_in_medical_treatment_facility": True,
        "ssi_medicaid_pays_majority_of_care": True,
    },
    "MD": {"md_paa_living_arrangement": "CARE_HOME_LEVEL_A"},
    "ME": {"me_ssp_living_arrangement": "ADULT_FOSTER_HOME"},
    "MN": {
        "mn_msa_living_arrangement": (
            "COUPLE_LIVING_WITH_OTHERS",
            "COUPLE_LIVING_WITH_OTHERS",
            "INDIVIDUAL_LIVING_WITH_OTHERS",
        )
    },
    "MO": {
        "mo_ssp_living_arrangement": "RCF_LEVEL_I",
        "mo_snc_facility_base_charge": 2_000,
    },
    "MT": {"mt_ssp_payment_category": "ASSISTED_LIVING_OR_GROUP_OR_COMMUNITY_HOME"},
    "NC": {"nc_sa_care_setting": "ADULT_CARE_HOME"},
    "NE": {"ne_aabd_alternate_living_arrangement": "ASSISTED_LIVING_FACILITY"},
    "NM": {"is_in_adult_residential_care": True},
    "OH": {"oh_rss_certified": True},
    "OR": {"or_ssp_category": "COMMUNITY_CARE"},
    "SC": {"is_in_residential_care_facility": True},
    "SD": {
        "sd_ssp_care_joint_entry": True,
        "sd_ssp_care_certified": True,
        "sd_ssp_care_setting": "ADULT_FOSTER_CARE",
        "sd_ssp_approved_care_cost": 1_500,
    },
    "TX": {
        "is_in_medicaid_facility": True,
        "ssi_lives_in_medical_treatment_facility": True,
        "ssi_medicaid_pays_majority_of_care": True,
    },
    "VA": {"va_ag_certified": True, "va_ag_is_joint_initial_month": True},
    "VT": {
        "vt_aabd_ep_level": ("PARTIAL_34", "PARTIAL_67", "FULL"),
        "vt_aabd_ep_nonspouse_essential_person": True,
    },
    "WI": {"wi_ssi_e_certified": True},
}

# Also reach California SSP with citizens in nonmedical care, the under-60
# Colorado program and the old Washington category for a disabled claimant
# with an ineligible spouse.
SUPPLEMENT_CASES = [(state, YEAR, "standard") for state in SUPPLEMENT_PROGRAMS] + [
    ("CA", YEAR, "ssi_ssp"),
    ("CO", YEAR, "and_cs"),
    ("IA", YEAR, "ia_dependent"),
    ("WA", 2022, "disabled"),
]
SUPPLEMENT_SCENARIO_INPUTS = {
    "ia_rcf": {
        "ia_ssa_category": "RESIDENTIAL_CARE",
        "ia_ssa_care_initial_partial_month": True,
        "ia_ssa_rcf_received_ssi_before_entry": True,
    },
    "ia_in_home": {
        "ia_ssa_category": "IN_HOME_CARE",
        "ia_ssa_ihhrc_monthly_cost": 400,
    },
    "ia_smme": {
        "ia_ssa_category": "SMME",
        "ia_ssa_smme_coverage_eligible": True,
        # Exercise the SMME payment rather than only its zero-income denial.
        "pension_income": (26_400, 26_400, 36_000),
        "ssi_countable_resources": (1_000, 1_000, 0),
    },
    "ia_dependent": {
        "ia_ssa_category": "DEPENDENT_PERSON",
        "ia_ssa_dependent_countable_income": 0,
    },
    "ssi_ssp": {
        "immigration_status_str": "CITIZEN",
        "ssi_qualifying_quarters_earnings": 40,
        "in_out_of_home_care_facility": True,
    },
    "and_cs": {
        "age": (50, 52, 70),
        "is_disabled": (True, True, False),
        "meets_ssi_disability_criteria": (True, True, False),
    },
    "disabled": {
        "age": (40, 40, 70),
        "is_disabled": (True, False, False),
        "meets_ssi_disability_criteria": (True, False, False),
    },
}


def _supplement_situation(
    system,
    state,
    pensions,
    ages,
    resources,
    care,
    third_care,
    explicit,
    year=YEAR,
    scenario="standard",
):
    names = ("claimant", "spouse", "third_adult")
    situation = {"people": {}}
    for index, name in enumerate(names):
        situation["people"][name] = {
            "age": {year: ages[index]},
            "pension_income": {year: 12 * pensions[index]},
            "ssi_countable_resources": {year: resources[index]},
            "is_tax_unit_head": {year: index == 0},
            "is_tax_unit_spouse": {year: index == 1},
            "is_tax_unit_dependent": {year: index == 2},
        }
    groups = {
        "household": "households",
        "tax_unit": "tax_units",
        "family": "families",
        "spm_unit": "spm_units",
    }
    for singular, plural in groups.items():
        situation[plural] = {singular: {"members": list(names)}}
    situation["households"]["household"]["state_code"] = {year: state}

    def set_inputs(inputs, members):
        for name, value in inputs.items():
            variable = system.variables[name]
            period = f"{year}-01" if variable.definition_period == "month" else year
            if variable.entity.is_person:
                for index, member in enumerate(names):
                    if member in members:
                        selected = value[index] if isinstance(value, tuple) else value
                        situation["people"][member][name] = {period: selected}
            else:
                entity = variable.entity.key
                situation[groups[entity]][entity][name] = {period: value}

    if care:
        set_inputs(
            SUPPLEMENT_CARE_INPUTS.get(state, {}), names if third_care else names[:2]
        )
    if state == "IA":
        if care:
            set_inputs(
                SUPPLEMENT_SCENARIO_INPUTS.get(scenario, {}),
                names if third_care else names[:2],
            )
    else:
        set_inputs(SUPPLEMENT_SCENARIO_INPUTS.get(scenario, {}), names)
    if explicit:
        situation["marital_units"] = {
            "couple": {"members": list(names[:2])},
            "single": {"members": [names[2]]},
        }
    return situation


def _supplement_amounts(
    state,
    pensions,
    ages,
    resources,
    care,
    third_care,
    explicit,
    year=YEAR,
    scenario="standard",
):
    # Reuse the same read-only system as the existing grids. Only simulations
    # and their caches are independent. Each has three people, so omitting
    # marital_units really uses the API's default unit, without mixing other
    # households or states into that default group.
    system = Simulation.default_tax_benefit_system_instance
    simulation = Simulation(
        situation=_supplement_situation(
            system,
            state,
            pensions,
            ages,
            resources,
            care,
            third_care,
            explicit,
            year,
            scenario,
        )
    )
    return {
        name: simulation.calculate(
            name,
            f"{year}-01"
            if system.variables[name].definition_period == "month"
            else year,
        )
        for name in SUPPLEMENT_PROGRAMS[state]
    }


@pytest.mark.parametrize(("state", "year", "scenario"), SUPPLEMENT_CASES)
@settings(
    max_examples=2,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow],
)
@example(
    pensions=(0, 0, 0),
    ages=(65, 65, 65),
    resources=(0, 0, 0),
    care=True,
    third_care=True,
    iowa_scenario="standard",
)
@example(
    pensions=(0, 497, 994),
    ages=(65, 64, 90),
    resources=(0, 0, 2_001),
    care=True,
    third_care=False,
    iowa_scenario="ia_rcf",
)
@example(
    pensions=(20, 65, 1_491),
    ages=(90, 65, 64),
    resources=(2_000, 0, 3_001),
    care=True,
    third_care=True,
    iowa_scenario="ia_in_home",
)
@example(
    pensions=(994, 1_491, 20),
    ages=(65, 90, 65),
    resources=(3_000, 0, 0),
    care=False,
    third_care=False,
    iowa_scenario="standard",
)
@example(
    pensions=(0, 0, 0),
    ages=(65, 65, 90),
    resources=(7_000, 1_000, 5_000),
    care=True,
    third_care=True,
    iowa_scenario="ia_smme",
)
@given(
    pensions=st.tuples(*(st.integers(0, 1_600) for _ in range(3))),
    ages=st.tuples(*(st.sampled_from((64, 65, 90)) for _ in range(3))),
    resources=st.tuples(*(st.integers(0, 8_000) for _ in range(3))),
    care=st.booleans(),
    third_care=st.booleans(),
    iowa_scenario=st.sampled_from(("standard", "ia_rcf", "ia_in_home", "ia_smme")),
)
def test_state_supplements_do_not_depend_on_omitted_marital_units(
    state, year, scenario, pensions, ages, resources, care, third_care, iowa_scenario
):
    """A third adult never becomes a spouse through the default group.

    YAML checks each state's independently calculated payment. This compares
    two API representations of the same people and marriage, including
    ineligible spouses, a third adult in a different care category, income
    exclusions/deeming edges, and the individual/couple resource limits.
    """
    if state == "IA" and scenario == "standard":
        scenario = iowa_scenario
    default = _supplement_amounts(
        state, pensions, ages, resources, care, third_care, False, year, scenario
    )
    explicit = _supplement_amounts(
        state, pensions, ages, resources, care, third_care, True, year, scenario
    )
    for name in SUPPLEMENT_PROGRAMS[state]:
        np.testing.assert_allclose(
            default[name], explicit[name], atol=0.01, err_msg=f"{state}: {name}"
        )


# These states preserve a declared marriage for at least one separated-spouse
# supplement budget. The cited YAML cases check that those budgets retain
# both spouses; this property separately checks that a household member who
# is not a spouse cannot alter them.
# CO: 9 CCR 2503-5 3.533(A)(2)(c), 3.534(B)-(C).
# MO: RSMo 208.010.1; DSS Manual 1035.005.00 (medical/nursing separation).
# OR: OAR 461-155-0630(3), hub ruling
# us-or:ssp-community-care-spouses-separate-facilities.
# SD: ARSD 67:46:04:10(6), 67:46:05:30 (joint care-entry month).
# VA: AG Manual Chapter B section 6 (first moment of the initial month).
# IA: 6-B Spouses Living Separately p.60 (prior-SSI RCF entry month).
SEPARATED_SUPPLEMENT_STATES = ("CO", "MO", "OR", "SD", "VA", "IA")
SEPARATED_PERIOD = "2026-07"


def _retained_state_pair_situation():
    situation = _income_situation([(0, 0, 0)])
    names = ("c0", "s0")
    for name in names:
        situation["people"][name].update(
            {
                "is_tax_unit_head": {YEAR: True},
                "is_tax_unit_spouse": {YEAR: False},
                "is_tax_unit_dependent": {YEAR: False},
            }
        )
    for plural in ("tax_units", "families", "spm_units", "households"):
        situation[plural] = {name: {"members": [name]} for name in names}
    for household in situation["households"].values():
        household["state_code"] = {YEAR: "IA"}
    return situation


def test_retained_state_spouse_helpers_keep_separated_marriage():
    """Exercise the helpers without calculating a state's whole grant chain."""
    simulation = Simulation(situation=_retained_state_pair_situation())
    person = simulation.get_population("people")
    year = make_period(YEAR)
    np.testing.assert_array_equal(state_is_married(person, year), [True, True])
    np.testing.assert_array_equal(
        state_couple_total(person, year, np.array([175, 100])), [275, 275]
    )


def test_retained_state_spouse_helpers_exclude_cross_household_parent():
    """A parent link alone excludes a pair across households and tax units."""
    situation = _retained_state_pair_situation()
    del situation["marital_units"]
    situation["people"]["c0"]["person_id"] = {YEAR: 1}
    situation["people"]["s0"]["person_id"] = {YEAR: 2}
    situation["people"]["s0"]["parent_1_id"] = {YEAR: 1}
    simulation = Simulation(situation=situation)
    person = simulation.get_population("people")
    year = make_period(YEAR)
    np.testing.assert_array_equal(state_is_married(person, year), [False, False])
    np.testing.assert_array_equal(
        state_couple_total(person, year, np.array([175, 100])), [175, 100]
    )


def test_retained_state_spouse_helpers_prefer_co_resident_parent_identity():
    """A co-resident parent's id cannot identify the remote spouse instead.

    Ids may repeat across households when every tax unit stays within its
    household and no claiming tax unit is set. The declared marriage spans
    households, but the claimant's parent link names the co-resident parent.
    """
    situation = _retained_state_pair_situation()
    situation["people"]["c0"].update(person_id={YEAR: 1}, parent_1_id={YEAR: 2})
    situation["people"]["s0"]["person_id"] = {YEAR: 2}
    situation["people"]["parent"] = {
        "age": {YEAR: 95},
        "person_id": {YEAR: 2},
        "is_tax_unit_head": {YEAR: True},
        "is_tax_unit_spouse": {YEAR: False},
        "is_tax_unit_dependent": {YEAR: False},
    }
    for plural in ("tax_units", "families", "spm_units", "marital_units"):
        situation[plural]["parent"] = {"members": ["parent"]}
    situation["households"]["c0"]["members"].append("parent")
    simulation = Simulation(situation=situation)
    person = simulation.get_population("people")
    year = make_period(YEAR)
    np.testing.assert_array_equal(state_is_married(person, year), [True, True, False])
    np.testing.assert_array_equal(
        state_couple_total(person, year, np.array([175, 100, 500])), [275, 275, 500]
    )


def _separated_supplement_situation(
    system,
    state,
    pensions,
    ages,
    resources,
    care,
    joint_entry,
    third_care,
    third_household,
    add_third,
):
    situation = _supplement_situation(
        system,
        state,
        pensions,
        ages,
        resources,
        care,
        third_care,
        True,
        scenario="ia_rcf" if state == "IA" else "standard",
    )
    names = ("claimant", "spouse", "third_adult")
    if not add_third:
        del situation["people"][names[2]]
        names = names[:2]

    for person in situation["people"].values():
        # Use assets as a primitive input, so SSI resource eligibility is
        # derived alongside federal income, couple status and payments.
        person["bank_account_assets"] = person.pop("ssi_countable_resources")
        person["is_tax_unit_head"] = {YEAR: True}
        person["is_tax_unit_spouse"] = {YEAR: False}
        person["is_tax_unit_dependent"] = {YEAR: False}
        for values in person.values():
            if PERIOD in values:
                values[SEPARATED_PERIOD] = values.pop(PERIOD)

    # Copy entity inputs, then give everyone independent nonmarital budgets.
    # An unrelated adult shares only the chosen household. The marriage is
    # always the same explicit two-person unit spanning the two households.
    for plural in ("tax_units", "families", "spm_units"):
        original = next(iter(situation[plural].values()))
        inputs = {name: value for name, value in original.items() if name != "members"}
        situation[plural] = {name: {**inputs, "members": [name]} for name in names}
    household = situation["households"]["household"]
    household_inputs = {
        name: value for name, value in household.items() if name != "members"
    }
    situation["households"] = {
        name: {**household_inputs, "members": [name]} for name in names[:2]
    }
    if add_third:
        situation["households"][names[third_household]]["members"].append(names[2])
    situation["marital_units"] = {"couple": {"members": list(names[:2])}}
    if add_third:
        situation["marital_units"]["single"] = {"members": [names[2]]}

    entry_input = {
        "SD": "sd_ssp_care_joint_entry",
        "VA": "va_ag_is_joint_initial_month",
    }.get(state)
    for index, name in enumerate(names):
        person = situation["people"][name]
        if entry_input:
            person[entry_input] = {
                SEPARATED_PERIOD: joint_entry and care and (index < 2 or third_care)
            }
        if care and (index < 2 or third_care):
            if state == "SD":
                person["sd_ssp_approved_care_cost"] = {SEPARATED_PERIOD: 2_000}
            elif state == "OR":
                # OAR 461-140-0040(5)(e)(D): inaccessible income is excluded.
                # This primitive keeps the community-care payment positive
                # when modeled SSI would otherwise fill the federal standard.
                person["or_ssp_inaccessible_income"] = {
                    SEPARATED_PERIOD: (194, 94, 0)[index]
                }
            elif state == "IA":
                person["ia_ssa_care_initial_partial_month"] = {
                    SEPARATED_PERIOD: joint_entry
                }
    return situation


def _assert_separated_care_budget(simulation, state, pensions, amounts):
    """An independent spouse-budget check in the existing simulations.

    Removing the spouse in both representations would satisfy the unrelated
    adult comparison. These generated ranges make the legally shared budget
    observable: low resources, eligible ages and unequal pensions; Oregon
    instead keeps modeled SSI positive for both community-care residents.
    No extra simulation or parameter-tree construction is needed.
    """
    if state == "MO":
        # RSMo 208.010.1 retains the couple resource test during medical
        # separation. The claimant is above the individual limit, while the
        # combined resources remain below the couple limit.
        assert np.all(
            simulation.calculate("mo_ssp_resource_eligible", SEPARATED_PERIOD)[:2]
        )
    elif state == "OR":
        # OAR 461-155-0630(3): two SSI community-care spouses qualify even in
        # separate facilities. Their own income after the documented
        # inaccessible amounts is below the individual standard, so neither
        # spouse has an excess to subtract from the other's payment.
        own = np.asarray(pensions[:2])
        federal = np.maximum(INDIVIDUAL_FBR - np.maximum(own - GENERAL_EXCLUSION, 0), 0)
        assert np.all(federal > 0)
        expected = INDIVIDUAL_FBR - (own + federal - np.array([194, 94]))
        np.testing.assert_allclose(amounts["or_ssp"], expected, atol=0.01)
    elif state == "SD":
        # ARSD 67:46:04:10(6), 67:46:06:03: both initial-month residents
        # contribute half their combined income. These pensions eliminate
        # SSI and stay below the entered $2,000 approved foster-care cost.
        expected = 2_000 - sum(pensions[:2]) / 2
        np.testing.assert_allclose(amounts["sd_ssp"], expected, atol=0.01)
    elif state == "VA":
        # AG Manual Chapter B section 6: initial-month spouses share the
        # combined income after one $20 exclusion. Neither receives SSI in
        # these ranges, so the AG's own countable-income budget applies.
        expected = (sum(pensions[:2]) - GENERAL_EXCLUSION) / 2
        np.testing.assert_allclose(
            simulation.calculate("va_ag_countable_income", SEPARATED_PERIOD)[:2],
            expected,
            atol=0.01,
        )
    elif state == "IA":
        # 6-B p.60 retains the prior-SSI couple's RCF entry-month budget.
        # Care does not apply the general exclusion; with current SSI zero,
        # each resident counts half the combined pension income.
        assert np.all(
            simulation.calculate("ia_ssa_rcf_couple_budget", SEPARATED_PERIOD)[:2]
        )
        np.testing.assert_allclose(
            simulation.calculate("ia_ssa_care_countable_income", SEPARATED_PERIOD)[:2],
            sum(pensions[:2]) / 2,
            atol=0.01,
        )
    else:
        # 9 CCR 2503-5 3.533(A)(2)(c): Colorado divides a married client's
        # $20 unearned-income disregard even when the spouses live apart.
        np.testing.assert_allclose(
            simulation.calculate("co_oap_own_countable_income", SEPARATED_PERIOD)[:2],
            np.asarray(pensions[:2]) - GENERAL_EXCLUSION / 2,
            atol=0.01,
        )


@pytest.mark.parametrize("state", SEPARATED_SUPPLEMENT_STATES)
@settings(
    max_examples=2,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow],
)
@example(
    pensions=(0, 0, 1_491),
    ages=(65, 65, 90),
    resources=(7_000, 1_000, 5_000),
    care=True,
    joint_entry=True,
    third_care=False,
    third_household=0,
    check_care_budget=False,
)
@example(
    pensions=(20, 65, 0),
    ages=(90, 65, 64),
    resources=(1_000, 15_000, 0),
    care=True,
    joint_entry=False,
    third_care=True,
    third_household=1,
    check_care_budget=False,
)
@example(
    pensions=(1_200, 1_200, 3_000),
    ages=(65, 65, 90),
    resources=(0, 0, 3_001),
    care=True,
    joint_entry=True,
    third_care=False,
    third_household=0,
    check_care_budget=False,
)
@example(
    pensions=(1_800, 1_200, 20),
    ages=(65, 90, 65),
    resources=(1_600, 1_400, 2_001),
    care=True,
    joint_entry=True,
    third_care=True,
    third_household=1,
    check_care_budget=False,
)
@example(
    pensions=(0, 0, 994),
    ages=(65, 65, 65),
    resources=(1_600, 1_600, 0),
    care=True,
    joint_entry=True,
    third_care=True,
    third_household=0,
    check_care_budget=False,
)
@example(
    pensions=(994, 1_491, 20),
    ages=(65, 64, 90),
    resources=(2_000, 0, 0),
    care=False,
    joint_entry=False,
    third_care=False,
    third_household=1,
    check_care_budget=False,
)
@given(
    pensions=st.tuples(
        st.integers(1_100, 1_400), st.integers(1_600, 1_800), st.integers(0, 3_000)
    ),
    ages=st.tuples(
        st.sampled_from((65, 90)),
        st.sampled_from((65, 90)),
        st.sampled_from((64, 65, 90)),
    ),
    resources=st.tuples(
        st.integers(0, 1_000), st.integers(0, 1_000), st.integers(0, 16_000)
    ),
    care=st.just(True),
    joint_entry=st.just(True),
    third_care=st.booleans(),
    third_household=st.integers(0, 1),
    check_care_budget=st.just(True),
)
def test_separated_spouses_supplements_ignore_unrelated_household_adult(
    state,
    pensions,
    ages,
    resources,
    care,
    joint_entry,
    third_care,
    third_household,
    check_care_budget,
):
    """A third adult cannot change either separately housed spouse's grant.

    YAML checks worked legal computations. The generated cases always enter
    a care or joint-entry budget and check it independently, so losing the
    spouse identically in both simulations is also detected. This comparison
    needs the simulation API to add a person while preserving the explicit
    marriage across two households and the spouses' independent other units.
    Both simulations share only the read-only system; caches stay separate.
    """
    if check_care_budget:
        if state == "OR":
            pensions = (pensions[0] - 1_000, pensions[1] - 1_000, pensions[2])
        elif state == "MO":
            resources = (resources[0] + 6_500, resources[1], resources[2])
    system = Simulation.default_tax_benefit_system_instance
    amounts = []
    for add_third in (False, True):
        simulation = Simulation(
            situation=_separated_supplement_situation(
                system,
                state,
                pensions,
                ages,
                resources,
                care,
                joint_entry,
                third_care,
                third_household,
                add_third,
            )
        )
        amounts.append(
            {
                name: simulation.calculate(
                    name,
                    SEPARATED_PERIOD
                    if system.variables[name].definition_period == "month"
                    else YEAR,
                )[:2]
                for name in SUPPLEMENT_PROGRAMS[state]
            }
        )
        if check_care_budget:
            _assert_separated_care_budget(simulation, state, pensions, amounts[-1])
    for name in SUPPLEMENT_PROGRAMS[state]:
        np.testing.assert_allclose(
            amounts[0][name], amounts[1][name], atol=0.01, err_msg=f"{state}: {name}"
        )


@pytest.mark.parametrize("state", ("MO", "OR", "SD", "VA", "IA"))
@pytest.mark.parametrize("relationship", ("parent", "dependent"))
@settings(
    max_examples=2,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow],
)
@given(
    pensions=st.tuples(st.integers(0, 300), st.integers(400, 600)),
    resources=st.tuples(st.integers(1_501, 2_000), st.integers(1_501, 2_000)),
    child_age=st.integers(65, 70),
    parent_first=st.booleans(),
)
def test_separated_known_nonspouses_match_explicit_singletons(
    state, relationship, pensions, resources, child_age, parent_first
):
    """A default two-person unit cannot marry known nonspouses living apart.

    Parent links and dependency are tested separately, so either exclusion
    being dropped is observable. Both representations have the same entry
    and care facts; only their marital-unit representation differs.
    """
    system = Simulation.default_tax_benefit_system_instance
    default = _separated_supplement_situation(
        system,
        state,
        (*pensions, 0),
        (child_age + 30, child_age, 65),
        (*resources, 0),
        care=True,
        joint_entry=True,
        third_care=False,
        third_household=0,
        add_third=False,
    )
    del default["marital_units"]
    names = ("claimant", "spouse")
    parent, child = names if parent_first else names[::-1]
    default["people"][parent]["age"] = {YEAR: child_age + 30}
    default["people"][child]["age"] = {YEAR: child_age}
    if relationship == "parent":
        # Keep independent tax units: only the cross-household parent link
        # proves this pair cannot be spouses.
        default["people"][parent]["person_id"] = {YEAR: 1}
        default["people"][child]["person_id"] = {YEAR: 2}
        default["people"][child]["parent_1_id"] = {YEAR: 1}
    else:
        # A dependent and the person claiming them cannot be spouses, even
        # without a supplied parent link and after moving to separate homes.
        default["tax_units"] = {"family": {"members": list(names)}}
        default["people"][parent]["is_tax_unit_head"] = {YEAR: True}
        default["people"][child]["is_tax_unit_head"] = {YEAR: False}
        default["people"][child]["is_tax_unit_dependent"] = {YEAR: True}
    explicit = deepcopy(default)
    explicit["marital_units"] = {name: {"members": [name]} for name in names}
    amounts = []
    for situation in (default, explicit):
        simulation = Simulation(situation=situation)
        amounts.append(
            {
                name: simulation.calculate(name, SEPARATED_PERIOD)
                for name in SUPPLEMENT_PROGRAMS[state]
            }
        )
        if state == "IA":
            assert not np.any(
                simulation.calculate("ia_ssa_rcf_couple_budget", SEPARATED_PERIOD)
            )
    for name in SUPPLEMENT_PROGRAMS[state]:
        np.testing.assert_allclose(
            amounts[0][name], amounts[1][name], atol=0.01, err_msg=f"{state}: {name}"
        )
