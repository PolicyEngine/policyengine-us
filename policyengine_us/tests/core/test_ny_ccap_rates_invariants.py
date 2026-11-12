"""Check New York CCAP rate and payment bounds in batched populations.

Hypothesis varies county groups, providers, age bands, schedules, expenses,
eligibility and family shares. Each household has twins for the payment
flags and special-needs expense boundaries. Published rate-period counts
supply the legacy reference without calling the new rate formulas.

Python checks relationships across those twins and the person-to-SPM-unit
aggregation. YAML cases separately pin the published dollar amounts and
expense allocation. Simulations reuse the imported tax-benefit system;
three examples each calculate one population for January 2025.
"""

import numpy as np
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation
from policyengine_us.system import system

YEAR = 2025
MONTH = "2025-01"
TOLERANCE = dict(atol=0.01, rtol=3e-7)
GROUPS = ("GROUP_1", "GROUP_2", "GROUP_3", "GROUP_4")
PROVIDERS = ("DCC_SACC", "FDC_GFDC", "LE_GC", "LE_STD", "LE_ENH")
AGES = ("INFANT", "TODDLER", "PRESCHOOLER", "SCHOOL_AGE")
# Each schedule records hours/day, days/week and the published rate periods.
# At 12 hours, each day earns a further part-day period. At 18 hours,
# each day earns a further daily period; days six and seven also earn one.
SCHEDULES = (
    (0, 0, (0, 0, 0)),
    (3, 1, (0, 0, 1)),
    (5, 7, (0, 0, 7)),
    (6, 4, (0, 4, 0)),
    (8, 3, (0, 3, 0)),
    (6, 5, (1, 0, 0)),
    (8, 7, (1, 2, 0)),
    (12, 5, (1, 0, 5)),
    (18, 7, (1, 9, 0)),
)
LEGACY_NYC_ENHANCED = {
    "weekly": (280, 245, 228, 202),
    "daily": (56, 49, 46, 42),
    "part_day": (37, 33, 30, 28),
}
VARIANTS = (
    "default",
    "nontraditional",
    "homeless",
    "accredited",
    "differentials",
    "health",
    "training",
    "enhancements",
    "special",
    "unqualified",
    "at_regular",
    "below_regular",
    "special_differentials",
)
FLAGS = {
    "ny_ccap_nontraditional_hours": {
        "nontraditional",
        "differentials",
        "special_differentials",
    },
    "ny_ccap_accredited_provider": {
        "accredited",
        "differentials",
        "special_differentials",
    },
    "ny_ccap_enhanced_health": {"health", "enhancements"},
    "ny_ccap_enhanced_training": {"training", "enhancements"},
    "ny_ccap_special_needs_care": {
        "special",
        "unqualified",
        "at_regular",
        "below_regular",
        "special_differentials",
    },
}


@st.composite
def child(draw):
    return {
        "provider": draw(st.sampled_from(PROVIDERS)),
        "age": draw(st.sampled_from(AGES)),
        "schedule": draw(st.integers(0, len(SCHEDULES) - 1)),
        "eligible": draw(st.booleans()),
        "disabled": draw(st.booleans()),
    }


@st.composite
def household(draw):
    return {
        "group": draw(st.sampled_from(GROUPS)),
        "children": draw(st.lists(child(), min_size=1, max_size=2)),
        "expenses": draw(st.integers(0, 12_000)),
        "family_share": draw(st.integers(0, 20_000)),
    }


def _coverage_households():
    # Every example includes all county/provider pairs and each schedule.
    return [
        {
            "group": group,
            "children": [
                {
                    "provider": provider,
                    "age": AGES[(group_index + provider_index) % len(AGES)],
                    "schedule": (group_index * len(PROVIDERS) + provider_index)
                    % len(SCHEDULES),
                    "eligible": True,
                    "disabled": False,
                }
            ],
            "expenses": 10_000,
            "family_share": (0, 100, 20_000)[provider_index % 3],
        }
        for group_index, group in enumerate(GROUPS)
        for provider_index, provider in enumerate(PROVIDERS)
    ]


def _table_rate(parameters, group, provider, age, schedule, legacy=False):
    counts = SCHEDULES[schedule][2]
    total = 0
    for table_name, count in zip(("weekly", "daily", "part_day"), counts):
        if legacy and group == "GROUP_4" and provider == "LE_ENH":
            cell = LEGACY_NYC_ENHANCED[table_name][AGES.index(age)]
        else:
            cell = parameters.rates[table_name][group][provider][age]
        total += count * cell
    # The model converts weekly schedules using 52 weeks and 12 months.
    return total * 52 / 12


def _simulate(households, parameters):
    situation = {
        entity: {}
        for entity in (
            "people",
            "tax_units",
            "marital_units",
            "families",
            "spm_units",
            "households",
        )
    }
    rows = []
    for household_index, unit in enumerate(households):
        for variant in VARIANTS:
            unit_name = f"unit_{household_index}_{variant}"
            members = []
            child_rows = []
            for index, case in enumerate(unit["children"]):
                name = f"{unit_name}_child_{index}"
                members.append(name)
                regular = _table_rate(
                    parameters,
                    unit["group"],
                    case["provider"],
                    case["age"],
                    case["schedule"],
                )
                expense = unit["expenses"]
                if variant == "at_regular":
                    expense = regular
                elif variant == "below_regular":
                    expense = regular * 0.75
                disabled = case["disabled"]
                if variant in {
                    "special",
                    "at_regular",
                    "below_regular",
                    "special_differentials",
                }:
                    disabled = True
                elif variant == "unqualified":
                    disabled = False
                hours, days, _ = SCHEDULES[case["schedule"]]
                person = {
                    "age": {YEAR: (1, 2, 4, 8)[AGES.index(case["age"])]},
                    "is_disabled": {YEAR: disabled},
                    "childcare_provider_type_group": {YEAR: case["provider"]},
                    "ny_ccap_age_group": {YEAR: case["age"]},
                    "childcare_hours_per_day": {YEAR: hours},
                    "childcare_days_per_week": {YEAR: days},
                    "ny_ccap_eligible_child": {MONTH: case["eligible"]},
                    "ny_ccap_childcare_expenses": {MONTH: expense},
                }
                if variant == "at_regular":
                    # Store both sides through the same float32 input path.
                    person["ny_ccap_regular_market_rate"] = {MONTH: regular}
                # Omit false inputs so the default twins check their defaults.
                for flag, variants in FLAGS.items():
                    if variant in variants:
                        person[flag] = {YEAR: True}
                person_index = len(situation["people"])
                situation["people"][name] = person
                situation["marital_units"][name] = {"members": [name]}
                child_rows.append(
                    {
                        **case,
                        "person_index": person_index,
                        "expense": expense,
                        "regular": regular,
                        "legacy": _table_rate(
                            parameters,
                            unit["group"],
                            case["provider"],
                            case["age"],
                            case["schedule"],
                            legacy=True,
                        ),
                    }
                )
            for entity in ("tax_units", "families", "spm_units"):
                situation[entity][unit_name] = {"members": members}
            situation["spm_units"][unit_name].update(
                {
                    "ny_ccap_family_share": {MONTH: unit["family_share"]},
                    "spm_unit_pre_subsidy_childcare_expenses": {
                        YEAR: unit["expenses"]
                        * 12
                        * sum(
                            SCHEDULES[case["schedule"]][0] > 0
                            for case in unit["children"]
                        )
                    },
                }
            )
            situation["households"][unit_name] = {
                "members": members,
                "state_code": {YEAR: "NY"},
                "ny_ccap_county_group": {YEAR: unit["group"]},
                "is_homeless": {
                    YEAR: variant
                    in {"homeless", "differentials", "special_differentials"}
                },
            }
            rows.append({**unit, "variant": variant, "children": child_rows})
    return Simulation(situation=situation, tax_benefit_system=system), rows


@settings(
    max_examples=3,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)
@given(st.lists(household(), min_size=3, max_size=8))
def test_ny_ccap_rate_and_payment_invariants(generated):
    parameters = system.parameters(f"{MONTH}-01").gov.states.ny.ocfs.ccap
    simulation, rows = _simulate(_coverage_households() + generated, parameters)

    def calc(variable, period=MONTH):
        return np.asarray(simulation.calculate(variable, period), dtype=float)

    regular = calc("ny_ccap_regular_market_rate")
    market = calc("ny_ccap_market_rate")
    expenses = calc("ny_ccap_childcare_expenses")
    payment = calc("ny_ccap_payment_rate")
    center = calc("ny_ccap_day_care_center_rate")
    differential = calc("ny_ccap_differential")
    benefit = calc("ny_ccap")
    default_indices = [
        case["person_index"]
        for row in rows
        if row["variant"] == "default"
        for case in row["children"]
    ]
    for flag in FLAGS:
        assert not calc(flag, YEAR)[default_indices].any()
    assert np.isfinite(benefit).all() and (benefit >= 0).all()
    assert (payment >= 0).all()
    assert ((differential >= 0) & (differential <= 0.25 + 1e-7)).all()
    # Every payment stays within the ordinary 25% differential ceiling.
    assert (payment <= np.minimum(expenses, market) * 1.25 + 0.01).all()

    for row_index, row in enumerate(rows):
        indices = [case["person_index"] for case in row["children"]]
        counted = np.array(
            [
                case["eligible"] and SCHEDULES[case["schedule"]][0] > 0
                for case in row["children"]
            ]
        )
        np.testing.assert_allclose(
            benefit[row_index],
            max(payment[indices][counted].sum() - row["family_share"], 0),
            **TOLERANCE,
        )
        for case in row["children"]:
            i = case["person_index"]
            if case["provider"] == "LE_GC":
                assert payment[i] <= center[i] + 0.01
            if row["variant"] == "default":
                if row["group"] == "GROUP_4" and case["provider"] == "LE_ENH":
                    # ACS's 75% informal rate intentionally exceeds main's 70%.
                    assert market[i] >= case["legacy"] - 0.01
                else:
                    np.testing.assert_allclose(market[i], case["legacy"], **TOLERANCE)
                np.testing.assert_allclose(regular[i], case["regular"], **TOLERANCE)
            if row["variant"] in {"special", "special_differentials"}:
                expected = regular[i] * (1.15 if expenses[i] > regular[i] else 1)
                np.testing.assert_allclose(market[i], expected, **TOLERANCE)
            elif row["variant"] in {"unqualified", "at_regular", "below_regular"}:
                np.testing.assert_allclose(market[i], regular[i], **TOLERANCE)
        if row["variant"] == "default":
            legacy_payment = sum(
                min(case["expense"], case["legacy"])
                for case, eligible in zip(row["children"], counted)
                if eligible
            )
            legacy_benefit = max(legacy_payment - row["family_share"], 0)
            has_nyc_enhanced = row["group"] == "GROUP_4" and any(
                case["provider"] == "LE_ENH" for case in row["children"]
            )
            if has_nyc_enhanced:
                assert benefit[row_index] >= legacy_benefit - 0.01
            else:
                np.testing.assert_allclose(
                    benefit[row_index], legacy_benefit, **TOLERANCE
                )

    # Each twin uses the same expenses, care and family share as its default.
    for start in range(0, len(rows), len(VARIANTS)):
        base = rows[start]
        base_indices = [case["person_index"] for case in base["children"]]
        for variant in (
            "nontraditional",
            "homeless",
            "accredited",
            "differentials",
            "health",
            "training",
            "enhancements",
        ):
            position = start + VARIANTS.index(variant)
            indices = [case["person_index"] for case in rows[position]["children"]]
            assert (payment[indices] >= payment[base_indices] - 0.01).all()
            assert benefit[position] >= benefit[start] - 0.01
