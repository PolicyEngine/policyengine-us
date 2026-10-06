"""Property tests: one claimant per household for the Montana elderly
homeowner/renter credit.

MCA 15-30-2341(1): "Only one claimant per household in a claim period under
the provisions of 15-30-2337 through 15-30-2341 is entitled to relief." The
2024 and 2025 Schedule 2EC attestation reads "I am the only member of my
household claiming this credit". Gross household income (line 18) covers
everyone in the household, so every tax unit in a household with a member
aged 62 or older computes its credit on the same net household income (line
22) and multiplier (line 29); the credits differ only by each tax unit's own
property tax (line 23) and rent (line 24). The model pays the tax unit whose
credit is largest.

A reference written here from the schedule's lines is compared with the
model for random Montana households of one to three tax units (single or
joint, any mix of ages, pension, interest, Social Security, property tax and
rent; no earned income, so no refundable credit enters line 8):

1. Each tax unit's credit before the limit matches the reference.
2. The household's credit is the largest of its tax units' credits, so it
   never exceeds the $1,150 cap of a single claim.
3. At most one tax unit per household is paid. Exactly one is selected in a
   household with an eligible tax unit, and none in a household without one.
4. A tax unit is paid either nothing or its whole credit, and the selected
   one is paid its whole credit.
5. Reversing the order of the tax units in a household does not change the
   household's credit.

The model computes in single precision, so comparisons allow one cent or
eight float32 spacings at the household's total income, whichever is larger.
"""

import numpy as np
import pytest

from policyengine_us import Simulation
from policyengine_us.system import system

YEAR = 2024
TOLERANCE = 0.01
P = system.parameters(YEAR).gov.states.mt.tax.income.credits.elderly_homeowner_or_renter


def build_situation(households):
    """Each household is a list of tax units; each tax unit is a dict with
    "adults" (a list of dicts with age, pension, interest and social
    security) and the head's property tax and rent. Every household is built
    twice: as given, and with its tax units in reverse order."""
    people, tax_units, marital_units, spm_units, families, situation_households = (
        {},
        {},
        {},
        {},
        {},
        {},
    )
    for h, units in enumerate(households):
        for order, ordered_units in (("fwd", units), ("rev", units[::-1])):
            key = f"{order}{h}"
            members = []
            for u, unit in enumerate(ordered_units):
                unit_key = f"{key}_u{u}"
                unit_members = []
                for a, adult in enumerate(unit["adults"]):
                    person = f"{unit_key}_p{a}"
                    people[person] = {
                        "age": {YEAR: adult["age"]},
                        "taxable_pension_income": {YEAR: adult["pension"]},
                        "taxable_interest_income": {YEAR: adult["interest"]},
                        "social_security_retirement": {YEAR: adult["social_security"]},
                        "is_tax_unit_dependent": {YEAR: False},
                    }
                    unit_members.append(person)
                # The first adult is the oldest, so the head: the property
                # tax and rent are theirs.
                head = unit_members[0]
                people[head]["real_estate_taxes"] = {YEAR: unit["property_tax"]}
                people[head]["rent"] = {YEAR: unit["rent"]}
                tax_units[unit_key] = {"members": unit_members}
                marital_units[unit_key] = {"members": unit_members}
                members += unit_members
            spm_units[key] = {"members": members}
            families[key] = {"members": members}
            situation_households[key] = {
                "members": members,
                "state_code": {YEAR: "MT"},
            }
    return {
        "people": people,
        "tax_units": tax_units,
        "marital_units": marital_units,
        "spm_units": spm_units,
        "families": families,
        "households": situation_households,
    }


def reference(units):
    """Each tax unit's credit before the one-claimant limit, from the 2024
    Schedule 2EC lines."""
    # Line 18: the pension, interest and Social Security of everyone in the
    # household.
    gross = sum(
        adult["pension"] + adult["interest"] + adult["social_security"]
        for unit in units
        for adult in unit["adults"]
    )
    # Lines 19-22.
    reduced = max(gross - P.net_household_income.standard_exclusion, 0)
    net = reduced * float(P.net_household_income.reduction_rate.calc(reduced))
    # Line 29.
    multiplier = float(P.multiplier.calc(gross))
    credits = []
    for unit in units:
        eligible = max(adult["age"] for adult in unit["adults"]) >= P.age_threshold
        # Lines 23-28.
        housing = unit["property_tax"] + unit["rent"] * P.rent_equivalent_tax_rate
        capped = min(max(housing - net, 0), P.cap)
        credits.append(eligible * capped * multiplier)
    return gross, credits


def tolerance(amount):
    return max(TOLERANCE, 8 * float(np.spacing(np.float32(abs(amount)))))


def calculate(households):
    """Per tax unit, in situation order: the credit before the limit, the
    selection and the credit."""
    simulation = Simulation(situation=build_situation(households))

    def by_tax_unit(variable):
        return np.asarray(simulation.calculate(variable, YEAR, map_to="tax_unit"))

    return {
        "pre_one_claimant": by_tax_unit(
            "mt_elderly_homeowner_or_renter_credit_pre_one_claimant"
        ),
        "selected": np.asarray(
            simulation.calculate(
                "mt_elderly_homeowner_or_renter_credit_selected_claimant", YEAR
            )
        ),
        "credit": by_tax_unit("mt_elderly_homeowner_or_renter_credit"),
    }


def assert_properties(households):
    result = calculate(households)
    start = 0
    for units in households:
        n = len(units)
        gross, expected = reference(units)
        tol = tolerance(gross)
        totals = {}
        for order, ordered_expected in (("fwd", expected), ("rev", expected[::-1])):
            pre = result["pre_one_claimant"][start : start + n]
            selected = result["selected"][start : start + n]
            credit = result["credit"][start : start + n]
            start += n
            # 1. Each tax unit's credit before the limit.
            assert pre == pytest.approx(ordered_expected, abs=tol), units
            # 2. The household is paid its largest credit, within the cap.
            totals[order] = credit.sum()
            assert totals[order] == pytest.approx(max(expected), abs=tol), units
            assert -tol <= totals[order] <= P.cap + tol, units
            # 3. At most one payment; one selection where any tax unit is
            # eligible.
            assert (credit > tol).sum() <= 1, units
            any_eligible = any(
                max(adult["age"] for adult in unit["adults"]) >= P.age_threshold
                for unit in units
            )
            assert selected.sum() == int(any_eligible), units
            # 4. Nothing or the whole credit; the selected unit gets it all.
            assert np.all((np.abs(credit) <= tol) | (np.abs(credit - pre) <= tol)), (
                units
            )
            assert credit[selected] == pytest.approx(pre[selected], abs=tol), units
        # 5. The order of the tax units does not matter.
        assert totals["fwd"] == pytest.approx(totals["rev"], abs=tol), units


def adult(age, pension=0, interest=0, social_security=0):
    return {
        "age": age,
        "pension": pension,
        "interest": interest,
        "social_security": social_security,
    }


def test_worked_example():
    """2024 Schedule 2EC: two siblings, 66 and 70, filing separately in one
    household with pensions of 10,000 and 15,000 and rent of 4,800 and
    7,200. Line 18 = 25,000; line 22 = 12,400 x 0.05 = 620. Line 27 is
    720 - 620 = 100 for the first and 1,080 - 620 = 460 for the second.
    Only the second is paid; before the limit the household received 560."""
    households = [
        [
            {"adults": [adult(66, pension=10_000)], "property_tax": 0, "rent": 4_800},
            {"adults": [adult(70, pension=15_000)], "property_tax": 0, "rent": 7_200},
        ]
    ]
    result = calculate(households)
    # Forward order, then reversed.
    assert result["pre_one_claimant"] == pytest.approx(
        [100, 460, 460, 100], abs=TOLERANCE
    )
    assert result["selected"].tolist() == [False, True, True, False]
    assert result["credit"] == pytest.approx([0, 460, 460, 0], abs=TOLERANCE)
    assert_properties(households)


try:
    import hypothesis
    import hypothesis.strategies as st
except ImportError:  # pragma: no cover
    hypothesis = None

if hypothesis is not None:
    # Each example builds a Simulation; on a loaded runner input generation
    # can trip the too_slow health check, which says nothing about the model.
    SLOW = [hypothesis.HealthCheck.too_slow]

    def amount(high):
        return st.one_of(st.just(0), st.integers(min_value=1, max_value=high))

    @st.composite
    def person(draw):
        return adult(
            draw(st.integers(min_value=40, max_value=90)),
            pension=draw(amount(25_000)),
            interest=draw(amount(15_000)),
            social_security=draw(amount(20_000)),
        )

    @st.composite
    def tax_unit(draw):
        adults = draw(st.lists(person(), min_size=1, max_size=2))
        # Put the oldest first so that the head holds the housing costs.
        adults.sort(key=lambda a: -a["age"])
        if len(adults) == 2 and adults[0]["age"] == adults[1]["age"]:
            adults[1]["age"] -= 1
        return {
            "adults": adults,
            "property_tax": draw(amount(4_000)),
            "rent": draw(amount(12_000)),
        }

    @hypothesis.settings(max_examples=15, deadline=None, suppress_health_check=SLOW)
    @hypothesis.given(
        st.lists(
            st.lists(tax_unit(), min_size=1, max_size=3),
            min_size=1,
            max_size=4,
        )
    )
    def test_properties(households):
        assert_properties(households)
