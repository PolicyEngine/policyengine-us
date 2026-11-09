"""Invariants for who receives the Alaska Permanent Fund Dividend and energy relief.

AS 43.23.005(a)(5) limits the dividend to citizens, lawful permanent residents,
refugees and asylees, and Alaska pays energy relief as part of the dividend
(sec. 13, ch. 34, SLA 2026). PolicyEngine also lets an input say a person does
not take up the dividend, for the statute's tests it has no input for. These
properties hold for every year and every mix of people in a household:

1. A person's dividend and energy relief each equal zero or the full amount
   for the year.
2. A person gets the dividend exactly when they live in Alaska, hold a status
   the statute names, and take it up. A status or take-up flag left unset
   counts as citizen and true, so a household calculation pays a resident
   unless an input says otherwise.
3. Energy relief passes through the same gate as the dividend.
4. Nobody outside Alaska gets either payment.
5. Turning one person's take-up off lowers that person's payment to zero and
   changes nobody else's.

ELIGIBLE_STATUSES restates AS 43.23.005(a)(5) here on purpose, so a change to
the parameter file that the statute does not support fails these tests. The
YAML tests pin examples. These tests run the real model on every status and
take-up combination, and on drawn years and household mixes, through one shared
tax-benefit system, so they build no extra model and load no dataset.
"""

from itertools import product

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation
from policyengine_us.system import system
from policyengine_us.tools.parameters import FIRST_MODELED_YEAR
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
STATES = ("AK", "WA")
LAST_YEAR = 2100
# 2015 starts the modeled years, 2022 and 2026 pay energy relief, and 2027 pays
# none.
EXHAUSTIVE_YEARS = (2015, 2022, 2026, 2027)

PERSON = st.tuples(
    st.sampled_from(STATES),
    st.sampled_from(STATUS_INPUTS),
    st.sampled_from(TAKE_UP_INPUTS),
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
    members = {state: [] for state in STATES}
    for index, (state, status, take_up) in enumerate(people):
        name = f"person_{index}"
        inputs = {}
        if status is not None:
            inputs["immigration_status"] = {year: status}
        if take_up is not None:
            inputs[TAKE_UP] = {year: take_up}
        situation_people[name] = inputs
        members[state].append(name)
    situation = {
        "people": situation_people,
        "households": {
            state: {"members": names, "state_code": {year: state}}
            for state, names in members.items()
            if names
        },
    }
    simulation = Simulation(situation=situation)
    # The results follow the order of situation_people, whatever the households.
    assert list(simulation.persons.ids) == list(situation_people)
    return (
        np.asarray(simulation.calculate("ak_permanent_fund_dividend", year)),
        np.asarray(simulation.calculate("ak_energy_relief", year)),
    )


def receives(state, status, take_up):
    return (
        state == "AK"
        and (status is None or status in ELIGIBLE_STATUSES)
        and take_up is not False
    )


def assert_gate_holds(year, people, dividend, energy_relief):
    full_dividend, full_energy_relief = amounts(year)
    for person, paid, relief in zip(people, dividend, energy_relief):
        expected = receives(*person)
        assert paid == pytest.approx(full_dividend if expected else 0, abs=0.005)
        assert relief == pytest.approx(full_energy_relief if expected else 0, abs=0.005)


def test_statuses_named_in_the_statute_exist_in_the_model():
    assert ELIGIBLE_STATUSES <= set(STATUSES)


@pytest.mark.parametrize("year", EXHAUSTIVE_YEARS)
def test_every_combination_of_state_status_and_take_up(year):
    people = list(product(STATES, STATUS_INPUTS, TAKE_UP_INPUTS))
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
    declined[target] = (*people[target][:2], False)
    dividend, energy_relief = calculate(year, people)
    new_dividend, new_energy_relief = calculate(year, declined)

    assert new_dividend[target] == 0
    assert new_energy_relief[target] == 0
    others = np.arange(len(people)) != target
    np.testing.assert_allclose(new_dividend[others], dividend[others], atol=0.005)
    np.testing.assert_allclose(
        new_energy_relief[others], energy_relief[others], atol=0.005
    )
