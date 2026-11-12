"""Invariants for who receives the Alaska Permanent Fund Dividend and energy relief.

Under AS 43.23.005(a)(5), Alaska limits the dividend to citizens, lawful
permanent residents, refugees and asylees, and it pays energy relief as part of
the dividend (sec. 13, ch. 34, SLA 2026). PolicyEngine also lets an input say a
person does not take up the dividend, to cover the statute's tests that
PolicyEngine cannot resolve from its other inputs. These properties hold for
every modeled year, every mix of people in a household and every age, unless an
input overrides the eligibility variable or a payment:

1. A person's dividend and energy relief each equal zero or the full amount
   for the year.
2. A person gets the dividend exactly when they live in Alaska, hold one of the
   statute's statuses, and take it up. An unset status counts as citizen and an
   unset take-up flag as true, so a household calculation pays a resident
   unless an input says otherwise. Age plays no part: age 0 does not show a
   birth during the dividend year.
3. Energy relief passes through the same gate as the dividend.
4. Nobody outside Alaska gets either payment.
5. Turning one person's take-up off lowers that person's payment to zero and
   changes nobody else's.

ELIGIBLE_STATUSES restates AS 43.23.005(a)(5), so these tests fail if someone
changes the parameter's statuses in a year these tests cover without changing
this file. The YAML tests pin examples. These tests run the real model on every
combination of state, status, take-up and representative age, and on drawn
years, states, ages and household mixes. They share one tax-benefit system, so
they build no extra model and load no dataset.
"""

from collections import defaultdict, namedtuple
from itertools import product

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation
from policyengine_us.system import system
from policyengine_us.tools.parameters import FIRST_MODELED_YEAR
from policyengine_us.variables.household.demographic.geographic.state_code import (
    StateCode,
)
from policyengine_us.variables.household.demographic.person.immigration_status import (
    ImmigrationStatus,
)

# AS 43.23.005(a)(5)(A) to (D).
ELIGIBLE_STATUSES = {"CITIZEN", "LEGAL_PERMANENT_RESIDENT", "REFUGEE", "ASYLEE"}
TAKE_UP = "takes_up_ak_permanent_fund_dividend_if_eligible"
STATUSES = tuple(status.name for status in ImmigrationStatus)
# None leaves the input unset, so the model's default applies.
STATUS_INPUTS = (None, *STATUSES)
TAKE_UP_INPUTS = (None, True, False)
# None leaves age at the model's default of 40. The rest straddle the ages where
# a mistaken child or newborn rule would change a payment.
AGE_INPUTS = (None, 0, 1, 17, 18, 65)
EXHAUSTIVE_STATES = ("AK", "WA")
ALL_STATES = tuple(state.name for state in StateCode)
LAST_YEAR = 2100
# 2015 starts the modeled years. Alaska paid energy relief in 2022 and 2026 and
# has appropriated none for 2027.
EXHAUSTIVE_YEARS = (2015, 2022, 2026, 2027)

Person = namedtuple("Person", ["state", "status", "take_up", "age"])
PERSON = st.builds(
    Person,
    # Half the draws land in Alaska, so the gate's positive cases stay common.
    st.one_of(st.just("AK"), st.sampled_from(ALL_STATES)),
    st.sampled_from(STATUS_INPUTS),
    st.sampled_from(TAKE_UP_INPUTS),
    st.one_of(st.sampled_from(AGE_INPUTS), st.integers(min_value=0, max_value=120)),
)
PEOPLE = st.lists(PERSON, min_size=1, max_size=10)
YEARS = st.integers(min_value=FIRST_MODELED_YEAR, max_value=LAST_YEAR)


def amounts(year):
    dor = system.parameters.gov.states.ak.dor
    instant = f"{year}-01-01"
    return float(dor.permanent_fund_dividend(instant)), float(
        dor.energy_relief(instant)
    )


def calculate(year, people):
    """Run the model with each state's people in one household."""
    situation_people = {}
    members = defaultdict(list)
    for index, person in enumerate(people):
        name = f"person_{index}"
        inputs = {}
        if person.status is not None:
            inputs["immigration_status"] = {year: person.status}
        if person.take_up is not None:
            inputs[TAKE_UP] = {year: person.take_up}
        if person.age is not None:
            inputs["age"] = {year: person.age}
        situation_people[name] = inputs
        members[person.state].append(name)
    situation = {
        "people": situation_people,
        "households": {
            state: {"members": names, "state_code": {year: state}}
            for state, names in members.items()
        },
    }
    simulation = Simulation(situation=situation)
    # The results follow the order of situation_people, whatever the households.
    assert list(simulation.persons.ids) == list(situation_people)
    return (
        np.asarray(simulation.calculate("ak_permanent_fund_dividend", year)),
        np.asarray(simulation.calculate("ak_energy_relief", year)),
    )


def receives(person):
    return (
        person.state == "AK"
        and (person.status is None or person.status in ELIGIBLE_STATUSES)
        and person.take_up is not False
    )


def assert_gate_holds(year, people, dividend, energy_relief):
    full_dividend, full_energy_relief = amounts(year)
    for person, paid, relief in zip(people, dividend, energy_relief):
        expected = receives(person)
        assert paid == pytest.approx(full_dividend if expected else 0, abs=0.005)
        assert relief == pytest.approx(full_energy_relief if expected else 0, abs=0.005)


def test_statuses_named_in_the_statute_exist_in_the_model():
    assert ELIGIBLE_STATUSES <= set(STATUSES)


@pytest.mark.parametrize("year", EXHAUSTIVE_YEARS)
def test_every_combination_of_state_status_take_up_and_age(year):
    people = [
        Person(*combination)
        for combination in product(
            EXHAUSTIVE_STATES, STATUS_INPUTS, TAKE_UP_INPUTS, AGE_INPUTS
        )
    ]
    assert_gate_holds(year, people, *calculate(year, people))


@settings(max_examples=25, deadline=None)
@given(YEARS, PEOPLE)
def test_payments_follow_the_gate_for_any_year_and_household_mix(year, people):
    assert_gate_holds(year, people, *calculate(year, people))


@settings(max_examples=15, deadline=None)
@given(YEARS, PEOPLE, st.integers(min_value=0))
def test_turning_take_up_off_only_removes_that_persons_payment(year, people, draw):
    target = draw % len(people)
    declined = list(people)
    declined[target] = people[target]._replace(take_up=False)
    dividend, energy_relief = calculate(year, people)
    new_dividend, new_energy_relief = calculate(year, declined)

    assert new_dividend[target] == 0
    assert new_energy_relief[target] == 0
    others = np.arange(len(people)) != target
    np.testing.assert_allclose(new_dividend[others], dividend[others], atol=0.005)
    np.testing.assert_allclose(
        new_energy_relief[others], energy_relief[others], atol=0.005
    )
