"""Hypothesis checks: what Vermont's child care subsidy saves the family.

From December 17, 2023, Vermont pays the provider the state rate less the family
share, whatever the provider charges (CCFAP Understanding Payments, question 3).
The family pays its share (question 1) and any charge above the state rate
(question 6). vt_ccfap holds the state's payment P, and vt_ccfap_family_benefit
holds the family's saving S. For generated families, in every month:

1. Bounds: 0 <= S <= P, and with a bill S <= the bill.
2. Accounting: over a year with a bill, childcare_expenses + child_care_subsidies
   = the bill, and household benefits count all of the subsidy and no more.
3. Differential: with a bill, what the family pays equals the guidance's rule,
   written here independently of the model. The family pays the share of the bill
   for any child CCFAP doesn't cover. For covered children it pays the family
   share plus any charge above the state rate, or the charge itself if that costs
   less. The first two hold for S = min(P, bill) too, so this one is what catches
   a subsidy that reads the state's payment.
4. Payment: from January 2024, P = max(sum of state rates - family share, 0)
   whatever the bill.
5. Dates: before December 17, 2023, Vermont paid the lesser of the two rates, so
   S = P. The model reads parameters at the start of each month, so December
   2023 falls under that rule. From January 2024, S = P when no covered child's
   charge sits below the state rate.
6. Monotonicity: with a bill, S never falls as the bill rises, and never rises as
   the family share rises. A zero bill stands apart, because the charge is unknown
   and the state rate stands in for it.
7. No bill: with no bill, S = P.

Each generated family is simulated in three variants (as drawn, with a larger
bill and with a larger family share) in one vectorized simulation per example.
The family share and the unit's eligibility are direct inputs here;
vt_ccfap_family_share.yaml and vt_ccfap_eligible.yaml pin those formulas.
"""

import numpy as np
import pytest

from policyengine_us import Simulation

hypothesis = pytest.importorskip("hypothesis")
st = pytest.importorskip("hypothesis.strategies")

WEEKS_IN_YEAR = 52
MONTHS_IN_YEAR = 12
TOLERANCE = 0.011
# A year with each rule: 2023 before the change (December included), and
# 2024 to 2026 after it. Vermont's rates change within 2024 and 2025.
YEARS = (2023, 2024, 2025, 2026)
PROVIDERS = ("LICENSED_CENTER", "REGISTERED_HOME")


child = st.fixed_dictionaries(
    {
        # Ages to 15 reach past the age limit, so the bill can fall on a child
        # CCFAP doesn't cover.
        "age": st.integers(0, 15),
        "dependent": st.sampled_from([True, True, True, False]),
        "provider": st.sampled_from(PROVIDERS),
        "days": st.integers(0, 5),
        "hours": st.integers(0, 12),
    }
)
family = st.fixed_dictionaries(
    {
        "children": st.lists(child, min_size=1, max_size=3),
        "bill": st.one_of(
            st.just(0),
            # Below and around a weekly family share and a state rate.
            st.integers(1, 6_000),
            st.integers(1, 90_000),
        ),
        "bill_rise": st.integers(1, 30_000),
        "weekly_share": st.one_of(st.just(0), st.integers(1, 450)),
        "share_rise": st.integers(1, 200),
        "eligible": st.sampled_from([True, True, True, False]),
    }
)
families = st.lists(family, min_size=3, max_size=6)


def variants(drawn):
    return {
        "base": drawn,
        "bill_rise": dict(drawn, bill=drawn["bill"] + drawn["bill_rise"]),
        "share_rise": dict(
            drawn, weekly_share=drawn["weekly_share"] + drawn["share_rise"]
        ),
    }


def by_month(year, value):
    return {f"{year}-{month:02d}": value for month in range(1, 13)}


def build(drawn_families, year):
    """One simulation holding every variant of every family."""
    people, spm_units, tax_units, families_, marital_units, households = (
        {} for _ in range(6)
    )
    order = []
    for n, drawn in enumerate(drawn_families):
        for variant, values in variants(drawn).items():
            unit = f"f{n}_{variant}"
            parent = f"{unit}_parent"
            children = [f"{unit}_child{i}" for i in range(len(values["children"]))]
            members = [parent, *children]
            people[parent] = {"age": {year: 30}}
            marital_units[parent] = {"members": [parent]}
            for name, kid in zip(children, values["children"]):
                people[name] = {
                    "age": {year: kid["age"]},
                    "is_tax_unit_dependent": {year: kid["dependent"]},
                    "vt_ccfap_provider_type": by_month(year, kid["provider"]),
                    "childcare_days_per_week": {year: kid["days"]},
                    "childcare_hours_per_day": {year: kid["hours"]},
                }
                marital_units[name] = {"members": [name]}
            monthly_share = values["weekly_share"] * WEEKS_IN_YEAR / MONTHS_IN_YEAR
            spm_units[unit] = {
                "members": members,
                "spm_unit_pre_subsidy_childcare_expenses": {year: values["bill"]},
                "vt_ccfap_family_share": by_month(year, monthly_share),
                "vt_ccfap_eligible": by_month(year, values["eligible"]),
            }
            tax_units[unit] = {"members": members}
            families_[unit] = {"members": members}
            households[unit] = {"members": members, "state_code": {year: "VT"}}
            order.append((n, variant))
    simulation = Simulation(
        situation={
            "people": people,
            "spm_units": spm_units,
            "tax_units": tax_units,
            "families": families_,
            "marital_units": marital_units,
            "households": households,
        }
    )
    return simulation, order


def unit_rows(simulation, order, year, month):
    """Per unit: the monthly payment, saving and share, and per child: the bill
    share, rate and whether the program covers the child."""
    # Each person's unit, by position: spm_unit_id doesn't tell units apart in a
    # household simulation.
    person_unit = simulation.populations["spm_unit"].members_entity_id
    age = simulation.calculate("age", year, map_to="person")
    is_child = simulation.calculate("is_child", year, map_to="person")
    period = f"{year}-{month:02d}"
    rate = simulation.calculate("vt_ccfap_state_rate", period, map_to="person")
    eligible_child = simulation.calculate(
        "vt_ccfap_eligible_child", period, map_to="person"
    )
    hours = simulation.calculate("childcare_hours_per_week", year, map_to="person")
    bill_share = simulation.calculate(
        "pre_subsidy_childcare_expenses", year, map_to="person"
    )
    payment = simulation.calculate("vt_ccfap", period)
    saving = simulation.calculate("vt_ccfap_family_benefit", period)
    share = simulation.calculate("vt_ccfap_family_share", period)
    eligible = simulation.calculate("vt_ccfap_eligible", period)
    annual_bill = simulation.calculate("spm_unit_pre_subsidy_childcare_expenses", year)
    rows = {}
    for index, key in enumerate(order):
        kids = np.asarray(person_unit == index) & np.asarray(is_child)
        rows[key] = {
            "payment": float(payment[index]),
            "saving": float(saving[index]),
            "share": float(share[index]),
            "eligible": bool(eligible[index]),
            "bill": float(annual_bill[index]),
            "rates": np.asarray(rate)[kids].astype(float),
            "charges": np.asarray(bill_share)[kids].astype(float) / WEEKS_IN_YEAR,
            "covered": np.asarray(eligible_child)[kids].astype(bool),
            "hours": np.asarray(hours)[kids].astype(float),
            "ages": np.asarray(age)[kids],
        }
    return rows


def monthly(weekly):
    return weekly * WEEKS_IN_YEAR / MONTHS_IN_YEAR


def monthly_out_of_pocket_per_guidance(row):
    """What the family pays in a month, from CCFAP Understanding Payments."""
    if not row["eligible"]:
        return row["bill"] / MONTHS_IN_YEAR
    uncovered = row["charges"][~row["covered"]].sum()
    charges = row["charges"][row["covered"]]
    rates = row["rates"][row["covered"]]
    above_rate = np.maximum(charges - rates, 0).sum()
    weekly_share = row["share"] * MONTHS_IN_YEAR / WEEKS_IN_YEAR
    return monthly(uncovered + min(charges.sum(), weekly_share + above_rate))


def assert_close(actual, expected, label):
    assert actual == pytest.approx(expected, abs=TOLERANCE), label


@hypothesis.settings(max_examples=12, deadline=None)
@hypothesis.given(
    drawn_families=families,
    year=st.sampled_from(YEARS),
    month=st.integers(1, 12),
)
def test_family_benefit_invariants(drawn_families, year, month):
    simulation, order = build(drawn_families, year)
    rows = unit_rows(simulation, order, year, month)
    pays_above_charge = (year, month) >= (2024, 1)
    for key, row in rows.items():
        label = f"{key} in {year}-{month:02d}: {row}"
        payment, saving = row["payment"], row["saving"]
        # 1. Bounds.
        assert -TOLERANCE <= saving <= payment + TOLERANCE, label
        if row["bill"] > 0:
            assert saving <= row["bill"] / MONTHS_IN_YEAR + TOLERANCE, label
            # 3. Differential.
            assert_close(
                row["bill"] / MONTHS_IN_YEAR - saving,
                monthly_out_of_pocket_per_guidance(row),
                label,
            )
        else:
            # 7. No bill.
            assert_close(saving, payment, label)
        in_care = (row["hours"] > 0) | (row["charges"] > 0)
        counted = row["covered"] & in_care
        if pays_above_charge:
            # 4. Payment.
            expected = (
                max(monthly(row["rates"][counted].sum()) - row["share"], 0)
                if row["eligible"]
                else 0
            )
            assert_close(payment, expected, label)
            # 5. Dates, from January 2024.
            charges_below_rate = (row["charges"] < row["rates"]) & counted
            if row["bill"] > 0 and not charges_below_rate.any():
                assert_close(saving, payment, label)
        else:
            # 5. Dates, before December 17, 2023.
            assert_close(saving, payment, label)
    # 6. Monotonicity.
    for n, _ in enumerate(drawn_families):
        base = rows[(n, "base")]
        if base["bill"] > 0:
            assert rows[(n, "bill_rise")]["saving"] >= base["saving"] - TOLERANCE
        assert rows[(n, "share_rise")]["saving"] <= base["saving"] + TOLERANCE


@hypothesis.settings(max_examples=6, deadline=None)
@hypothesis.given(drawn_families=families, year=st.sampled_from(YEARS))
def test_annual_accounting(drawn_families, year):
    simulation, order = build(drawn_families, year)
    bill = simulation.calculate("spm_unit_pre_subsidy_childcare_expenses", year)
    subsidy = simulation.calculate("child_care_subsidies", year)
    saving = simulation.calculate("vt_ccfap_family_benefit", year)
    counted = simulation.calculate("household_child_care_subsidies", year)
    out_of_pocket = simulation.calculate("childcare_expenses", year)
    has_children = simulation.calculate("is_child", year, map_to="spm_unit") > 0
    for index, key in enumerate(order):
        label = f"{key} in {year}"
        # 2. Accounting. The subsidy is the family's saving, and it never exceeds
        # the bill, so household benefits count all of it and the rest of the bill
        # stays with the family.
        assert_close(float(subsidy[index]), float(saving[index]), label)
        assert_close(float(counted[index]), float(subsidy[index]), label)
        if bill[index] > 0 and has_children[index]:
            assert_close(
                float(out_of_pocket[index]) + float(subsidy[index]),
                float(bill[index]),
                label,
            )
