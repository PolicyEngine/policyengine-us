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

YAML covers worked cases. Python is needed to check the for-all properties
over every ordered edge of the grids and to compare with an oracle that does
not use the model. Both grids share the read-only system singleton; neither
constructs a model per household. This file routes to the Rest/core group.
"""

from itertools import product
from pathlib import Path

import numpy as np
import pytest
import yaml
from hypothesis import HealthCheck, example, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

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


def _oracle_ssi(claimant_unearned, spouse_unearned, spouse_earned):
    """Monthly SSI for an aged claimant with an ineligible spouse.

    416.1163(d)(1): no deeming when the spouse's income is not more than the
    couple rate less the individual rate. (d)(2): otherwise the couple's
    combined countable income is subtracted from the couple rate. (e)(2): the
    benefit is the lesser of that and the individual rate less the claimant's
    own countable income.
    """
    alone = np.maximum(
        INDIVIDUAL_FBR
        - _countable(claimant_unearned, np.zeros_like(claimant_unearned)),
        0,
    )
    couple = np.maximum(
        COUPLE_FBR - _countable(claimant_unearned + spouse_unearned, spouse_earned),
        0,
    )
    deems = spouse_unearned + spouse_earned > COUPLE_FBR - INDIVIDUAL_FBR
    return np.where(deems, np.minimum(couple, alone), alone)


def _income_situation(rows):
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


def _income_ssi(rows):
    simulation = Simulation(situation=_income_situation(rows))
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
        ),
        min_size=40,
        max_size=40,
    )
)
def test_random_incomes_match_independent_oracle(rows):
    claimant_ssi, _, _ = _income_ssi(rows)
    expected = _oracle_ssi(*np.array(rows, dtype=float).T)
    np.testing.assert_allclose(claimant_ssi, expected, atol=0.01)


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
    ("WA", 2022, "disabled"),
]
SUPPLEMENT_SCENARIO_INPUTS = {
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
)
@example(
    pensions=(0, 497, 994),
    ages=(65, 64, 90),
    resources=(0, 0, 2_001),
    care=True,
    third_care=False,
)
@example(
    pensions=(20, 65, 1_491),
    ages=(90, 65, 64),
    resources=(2_000, 0, 3_001),
    care=True,
    third_care=True,
)
@example(
    pensions=(994, 1_491, 20),
    ages=(65, 90, 65),
    resources=(3_000, 0, 0),
    care=False,
    third_care=False,
)
@example(
    pensions=(0, 0, 0),
    ages=(65, 65, 90),
    resources=(7_000, 1_000, 5_000),
    care=True,
    third_care=True,
)
@given(
    pensions=st.tuples(*(st.integers(0, 1_600) for _ in range(3))),
    ages=st.tuples(*(st.sampled_from((64, 65, 90)) for _ in range(3))),
    resources=st.tuples(*(st.integers(0, 8_000) for _ in range(3))),
    care=st.booleans(),
    third_care=st.booleans(),
)
def test_state_supplements_do_not_depend_on_omitted_marital_units(
    state, year, scenario, pensions, ages, resources, care, third_care
):
    """A third adult never becomes a spouse through the default group.

    YAML checks each state's independently calculated payment. This compares
    two API representations of the same people and marriage, including
    ineligible spouses, a third adult in a different care category, income
    exclusions/deeming edges, and the individual/couple resource limits.
    """
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
