"""Invariants for Riverside County General Relief property and wage deductions.

Riverside compares a unit's combined property with one $500 limit, so each
asset counts once however many people are in the unit. Wage deductions are
what is withheld from each earner's own pay, so one member's deductions never
depend on another member's wages. Additional Medicare Tax is withheld from an
employee's wages above $200,000 without regard to filing status or a spouse's
wages (26 U.S.C. 3102(f)(1)).

Hypothesis draws batches of adult-only units (one to four members, each its
own SPM unit, tax unit and household in Riverside), and a seeded population of
120 units adds breadth. Each batch runs as one vectorized simulation, and
again with the first member's assets and wages raised. For every unit:

1. Property differential: countable property equals an independent numpy sum
   of the members' bank, stock and bond assets, vehicle value above the
   $4,650 exemption and the members' personal property. Property eligibility
   is that sum below $500.
2. Property monotone: raising one member's assets never lowers countable
   property.
3. Withholding bounds and differential: 0 <= additional_medicare_tax_withheld
   = 0.9% of wages above $200,000 <= 0.9% of wages, with the threshold and
   rate taken from the statute rather than the model's parameters. For a
   single filer it equals the Additional Medicare Tax liability.
4. Deduction differential: each member's monthly GR deductions equal their
   own Social Security, Medicare and Additional Medicare withholding plus
   their own CA withholding, divided by 12. Summed over a tax unit, the CA
   withholding is state_withheld_income_tax counted once.
5. Locality: raising the first member's wages leaves every other member's
   deductions unchanged.
"""

import numpy as np
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

TOLERANCE = 0.01  # dollars
YEAR = 2024
MONTH = "2024-01"

# Riverside DPSS General Assistance Eligibility manual pp. 22 and 25.
PROPERTY_LIMIT = 500
VEHICLE_EXEMPTION = 4_650
# 26 U.S.C. 3101(a), (b)(1), (b)(2) and 3102(f)(1); SSA 2024 wage base.
SOCIAL_SECURITY_RATE = 0.062
SOCIAL_SECURITY_WAGE_BASE = 168_600
MEDICARE_RATE = 0.0145
ADDITIONAL_MEDICARE_RATE = 0.009
ADDITIONAL_MEDICARE_WITHHOLDING_THRESHOLD = 200_000

assets = st.one_of(st.just(0.0), st.integers(1, 400).map(float))
wages = st.one_of(
    st.just(0.0),
    st.integers(1, 12_000).map(float),
    st.integers(12_000, 400_000).map(float),
)


@st.composite
def members(draw):
    return {
        "bank_account_assets": draw(assets),
        "stock_assets": draw(assets),
        "bond_assets": draw(assets),
        "personal_property": draw(assets),
        "employment_income": draw(wages),
    }


@st.composite
def units(draw):
    return {
        "members": draw(st.lists(members(), min_size=1, max_size=4)),
        "household_vehicles_value": draw(
            st.one_of(st.just(0.0), st.integers(4_000, 5_500).map(float))
        ),
        "raise": {
            "bank_account_assets": draw(assets),
            "employment_income": draw(wages),
        },
    }


SEED = 20261006


def _seeded_units(n=120):
    rng = np.random.default_rng(SEED)

    def amount(high):
        return float(rng.integers(1, high + 1)) if rng.random() < 0.6 else 0.0

    def wage():
        return [0.0, amount(12_000), float(rng.integers(12_000, 400_001))][
            rng.integers(0, 3)
        ]

    out = []
    for _ in range(n):
        out.append(
            {
                "members": [
                    {
                        "bank_account_assets": amount(400),
                        "stock_assets": amount(400),
                        "bond_assets": amount(400),
                        "personal_property": amount(400),
                        "employment_income": wage(),
                    }
                    for _ in range(int(rng.integers(1, 5)))
                ],
                "household_vehicles_value": (
                    float(rng.integers(4_000, 5_501)) if rng.random() < 0.5 else 0.0
                ),
                "raise": {
                    "bank_account_assets": amount(400),
                    "employment_income": wage(),
                },
            }
        )
    return out


def _situation(batch, *, raised):
    people = {}
    groups = {
        name: {}
        for name in [
            "tax_units",
            "spm_units",
            "families",
            "marital_units",
            "households",
        ]
    }
    for i, unit in enumerate(batch):
        names = []
        for j, values in enumerate(unit["members"]):
            name = f"person_{i}_{j}"
            values = dict(values)
            if raised and j == 0:
                for key, increase in unit["raise"].items():
                    values[key] += increase
            # Distinct ages fix head and spouse; any others are dependents.
            people[name] = {
                "age": 60 - 5 * j,
                "is_tax_unit_head": j == 0,
                "is_tax_unit_spouse": j == 1,
                "is_tax_unit_dependent": j > 1,
                **values,
            }
            names.append(name)
            groups["marital_units"][f"marital_unit_{i}_{j}"] = {"members": [name]}
        if len(names) > 1:
            for j in range(2):
                del groups["marital_units"][f"marital_unit_{i}_{j}"]
            groups["marital_units"][f"couple_{i}"] = {"members": names[:2]}
        groups["tax_units"][f"tax_unit_{i}"] = {"members": names}
        groups["spm_units"][f"spm_unit_{i}"] = {"members": names}
        groups["families"][f"family_{i}"] = {"members": names}
        groups["households"][f"household_{i}"] = {
            "members": names,
            "state_code": "CA",
            "in_riv": True,
            "household_vehicles_value": unit["household_vehicles_value"],
        }
    people = {
        name: {key: {YEAR: value} for key, value in values.items()}
        for name, values in people.items()
    }
    for group in groups.values():
        for values in group.values():
            for key in list(values):
                if key != "members":
                    values[key] = {YEAR: values[key]}
    return {"people": people, **groups}


PERSON_YEAR = [
    "bank_account_assets",
    "stock_assets",
    "bond_assets",
    "personal_property",
    "payroll_tax_gross_wages",
    "employee_social_security_tax",
    "employee_medicare_tax",
    "additional_medicare_tax_withheld",
    "ca_withheld_income_tax",
]


def _run(batch, *, raised=False):
    sim = Simulation(situation=_situation(batch, raised=raised))
    out = {
        name: np.asarray(sim.calculate(name, YEAR), dtype=float)
        for name in PERSON_YEAR
        + [
            "household_vehicles_value",
            "ca_riv_general_relief_countable_property_value",
            "ca_riv_general_relief_property_eligible",
            "state_withheld_income_tax",
            "additional_medicare_tax",
        ]
    }
    out["deductions"] = np.asarray(
        sim.calculate("ca_riv_general_relief_earned_income_deductions", MONTH),
        dtype=float,
    )
    out["filing_status"] = sim.calculate("filing_status", YEAR).decode_to_str()
    out["unit"] = sim.populations["spm_unit"].members_entity_id
    out["n_units"] = len(out["ca_riv_general_relief_countable_property_value"])
    out["first"] = np.array(
        [name.endswith("_0") for name in sim.populations["person"].ids]
    )
    return out


def _unit_sum(run, values):
    return np.bincount(run["unit"], weights=values, minlength=run["n_units"])


def _check(batch):
    base = _run(batch)

    # 1. Property differential.
    cash = _unit_sum(
        base,
        base["bank_account_assets"] + base["stock_assets"] + base["bond_assets"],
    )
    vehicles = np.maximum(base["household_vehicles_value"] - VEHICLE_EXEMPTION, 0)
    property_value = cash + vehicles + _unit_sum(base, base["personal_property"])
    countable = base["ca_riv_general_relief_countable_property_value"]
    np.testing.assert_allclose(countable, property_value, atol=TOLERANCE)
    np.testing.assert_array_equal(
        base["ca_riv_general_relief_property_eligible"].astype(bool),
        property_value < PROPERTY_LIMIT,
    )

    # 3. Withholding bounds and differential.
    wages = base["payroll_tax_gross_wages"]
    withheld = base["additional_medicare_tax_withheld"]
    expected_withheld = ADDITIONAL_MEDICARE_RATE * np.maximum(
        wages - ADDITIONAL_MEDICARE_WITHHOLDING_THRESHOLD, 0
    )
    np.testing.assert_allclose(withheld, expected_withheld, atol=TOLERANCE)
    assert (withheld >= 0).all()
    assert (withheld <= ADDITIONAL_MEDICARE_RATE * wages + TOLERANCE).all()
    # Each unit is one SPM unit and one tax unit, in the same order.
    unit = base["unit"]
    single = (base["filing_status"][unit] == "SINGLE") & (np.bincount(unit)[unit] == 1)
    np.testing.assert_allclose(
        withheld[single],
        base["additional_medicare_tax"][unit][single],
        atol=TOLERANCE,
    )

    # 4. Deduction differential and conservation.
    payroll = (
        SOCIAL_SECURITY_RATE * np.minimum(wages, SOCIAL_SECURITY_WAGE_BASE)
        + MEDICARE_RATE * wages
        + expected_withheld
    )
    np.testing.assert_allclose(
        base["deductions"],
        (payroll + base["ca_withheld_income_tax"]) / 12,
        atol=TOLERANCE,
    )
    np.testing.assert_allclose(
        _unit_sum(base, base["ca_withheld_income_tax"]),
        base["state_withheld_income_tax"],
        atol=TOLERANCE,
    )

    raised = _run(batch, raised=True)

    # 2. Property monotone.
    assert (
        raised["ca_riv_general_relief_countable_property_value"]
        >= countable - TOLERANCE
    ).all()

    # 5. Locality: only the first member's deductions may move.
    others = ~base["first"]
    np.testing.assert_allclose(
        raised["deductions"][others], base["deductions"][others], atol=TOLERANCE
    )


# A batch's cost is mostly per-variable overhead, so each example is a large
# batch and there are few examples.
SETTINGS = dict(
    max_examples=6,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)


@settings(**SETTINGS)
@given(st.lists(units(), min_size=5, max_size=25))
def test_riverside_general_relief_attribution_invariants(batch):
    _check(batch)


def test_seeded_population():
    _check(_seeded_units())
