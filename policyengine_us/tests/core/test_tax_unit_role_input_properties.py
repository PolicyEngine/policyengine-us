"""Properties of supplied tax-unit roles over generated units.

Invariants, each checked for every generated household:

1. Partition: every person is exactly one of head, spouse and dependent.
2. Supplied roles hold: in a unit whose roles are supplied, the role variables
   equal the supplied roles, so the unit has exactly one head and at most one
   spouse.
3. Fallback: in a unit without supplied roles, the roles equal an independent
   implementation of age ordering. The oldest adult heads the unit, earliest
   member on ties, skipping adults input as tax unit dependents unless every
   adult is one; the next such adult is the spouse unless any member of the
   unit is separated.
4. Filing status is computed: no supplied status is read, so a unit files
   jointly exactly when it has a spouse, supplied or inferred.
5. Workaround equivalence (differential): supplying roles through
   tax_unit_role_input gives the same filing status and income tax as setting
   is_tax_unit_head, is_tax_unit_spouse and is_tax_unit_dependent directly,
   the policyengine-taxsim workaround. Neither side sets filing_status, so both
   compute it from the same roles.
6. Error contract: supplied roles raise exactly when malformed - supplied for
   only some members, or not exactly one HEAD and at most one SPOUSE.
"""

from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st
import numpy as np
import pytest

from policyengine_us import Simulation

YEAR = 2024
SETTINGS = dict(
    derandomize=True,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)


@st.composite
def tax_units(draw, supplied=None, dependent_inputs=False):
    """One tax unit, with supplied roles when ``supplied`` (drawn if None).

    With ``dependent_inputs``, a unit without supplied roles also flags some
    members as input tax unit dependents, and a supplied unit flags exactly
    its supplied dependents.
    """
    size = draw(st.integers(1, 4))
    ages = draw(st.lists(st.integers(0, 90), min_size=size, max_size=size))
    separated = draw(
        st.lists(
            st.sampled_from([False, False, False, True]),
            min_size=size,
            max_size=size,
        )
    )
    earnings = draw(
        st.lists(st.sampled_from([0, 15_000, 60_000]), min_size=size, max_size=size)
    )
    with_roles = draw(st.booleans()) if supplied is None else supplied
    roles = None
    if with_roles:
        head = draw(st.integers(0, size - 1))
        others = [i for i in range(size) if i != head]
        spouse = None
        if others:
            spouse = draw(st.one_of(st.none(), st.sampled_from(others)))
        roles = ["DEPENDENT"] * size
        roles[head] = "HEAD"
        if spouse is not None:
            roles[spouse] = "SPOUSE"
    dependent_input = None
    if dependent_inputs:
        if roles:
            dependent_input = [role == "DEPENDENT" for role in roles]
        else:
            dependent_input = draw(
                st.lists(st.booleans(), min_size=size, max_size=size)
            )
    return dict(
        ages=ages,
        separated=separated,
        earnings=earnings,
        roles=roles,
        dependent_input=dependent_input,
    )


def _situation(units, pin_explicitly=False):
    people, tax_unit_groups = {}, {}
    for u, unit in enumerate(units):
        members = []
        for i, age in enumerate(unit["ages"]):
            name = f"u{u}p{i}"
            person = {
                "age": {YEAR: age},
                "is_separated": {YEAR: unit["separated"][i]},
                "employment_income": {YEAR: unit["earnings"][i]},
            }
            role = unit["roles"][i] if unit["roles"] else None
            if role and pin_explicitly:
                person["is_tax_unit_head"] = {YEAR: role == "HEAD"}
                person["is_tax_unit_spouse"] = {YEAR: role == "SPOUSE"}
                person["is_tax_unit_dependent"] = {YEAR: role == "DEPENDENT"}
            elif role:
                person["tax_unit_role_input"] = {YEAR: role}
            if unit["dependent_input"] is not None:
                person["is_tax_unit_dependent"] = {YEAR: unit["dependent_input"][i]}
            people[name] = person
            members.append(name)
        tax_unit_groups[f"u{u}"] = {"members": members}
    return {
        "people": people,
        "tax_units": tax_unit_groups,
        "households": {
            "household": {"members": list(people), "state_name": {YEAR: "TX"}}
        },
    }


def _age_rule(ages, separated, dependent_input=None):
    # Mirrors the fallback as it stands. Adults input as tax unit dependents
    # are skipped unless every adult is one (#9630). Any separated member
    # blocks every spouse; that unit-wide gate is a known defect (#9620), so
    # update this reference when it is fixed.
    adults = [i for i, age in enumerate(ages) if age >= 18]
    if dependent_input is not None:
        non_dependents = [i for i in adults if not dependent_input[i]]
        if non_dependents:
            adults = non_dependents
    head = min(adults, key=lambda i: (-ages[i], i)) if adults else None
    candidates = [] if any(separated) else [i for i in adults if i != head]
    spouse = min(candidates, key=lambda i: (-ages[i], i)) if candidates else None
    return head, spouse


def _by_unit(units, values):
    out, start = [], 0
    for unit in units:
        size = len(unit["ages"])
        out.append(list(values[start : start + size]))
        start += size
    return out


def _check_roles(units, head, spouse):
    for unit, h, s in zip(units, _by_unit(units, head), _by_unit(units, spouse)):
        if unit["roles"]:
            # 2. Supplied roles hold.
            assert h == [role == "HEAD" for role in unit["roles"]]
            assert s == [role == "SPOUSE" for role in unit["roles"]]
        else:
            # 3. Fallback equals the independent age-ordering rule.
            expected_head, expected_spouse = _age_rule(
                unit["ages"], unit["separated"], unit["dependent_input"]
            )
            assert h == [i == expected_head for i in range(len(h))]
            assert s == [i == expected_spouse for i in range(len(s))]


@settings(max_examples=40, **SETTINGS)
@given(st.lists(tax_units(), min_size=1, max_size=4))
def test_roles_follow_supplied_values_and_otherwise_age_ordering(units):
    simulation = Simulation(situation=_situation(units))
    head = simulation.calculate("is_tax_unit_head", YEAR).astype(bool)
    spouse = simulation.calculate("is_tax_unit_spouse", YEAR).astype(bool)
    dependent = simulation.calculate("is_tax_unit_dependent", YEAR).astype(bool)
    status = simulation.calculate("filing_status", YEAR).decode_to_str().tolist()
    # 1. Partition.
    assert np.all(head.astype(int) + spouse.astype(int) + dependent.astype(int) == 1)
    _check_roles(units, head, spouse)
    for s, unit_status in zip(_by_unit(units, spouse), status):
        # 4. Filing status is computed: joint exactly when there is a spouse.
        assert (unit_status == "JOINT") == any(s)


@settings(max_examples=40, **SETTINGS)
@given(st.lists(tax_units(dependent_inputs=True), min_size=1, max_size=4))
def test_supplied_roles_compose_with_input_dependents(units):
    # Every person carries an is_tax_unit_dependent input, as a situation that
    # sets it for anyone must. Supplied units flag exactly their supplied
    # dependents; the others skip their flagged adults when inferring roles.
    simulation = Simulation(situation=_situation(units))
    head = simulation.calculate("is_tax_unit_head", YEAR).astype(bool)
    spouse = simulation.calculate("is_tax_unit_spouse", YEAR).astype(bool)
    assert not np.any(head & spouse)
    _check_roles(units, head, spouse)


@settings(max_examples=15, **SETTINGS)
@given(st.lists(tax_units(supplied=True), min_size=1, max_size=3))
def test_supplied_roles_match_the_explicit_pin(units):
    # 5. Differential: the role input and a complete explicit pin agree.
    supplied = Simulation(situation=_situation(units))
    pinned = Simulation(situation=_situation(units, pin_explicitly=True))
    assert (
        supplied.calculate("filing_status", YEAR).decode_to_str().tolist()
        == pinned.calculate("filing_status", YEAR).decode_to_str().tolist()
    )
    np.testing.assert_allclose(
        supplied.calculate("income_tax", YEAR),
        pinned.calculate("income_tax", YEAR),
        atol=0.005,
    )


@settings(max_examples=40, **SETTINGS)
@given(
    st.lists(
        st.sampled_from([None, "HEAD", "SPOUSE", "DEPENDENT"]),
        min_size=1,
        max_size=4,
    )
)
def test_supplied_roles_raise_exactly_when_malformed(roles):
    people = {
        f"p{i}": {
            "age": {YEAR: 40},
            **({"tax_unit_role_input": {YEAR: r}} if r else {}),
        }
        for i, r in enumerate(roles)
    }
    situation = {
        "people": people,
        "tax_units": {"unit": {"members": list(people)}},
        "households": {"household": {"members": list(people)}},
    }
    supplied = [r is not None for r in roles]
    malformed = (any(supplied) and not all(supplied)) or (
        all(supplied) and (roles.count("HEAD") != 1 or roles.count("SPOUSE") > 1)
    )
    # 6. Error contract.
    simulation = Simulation(situation=situation)
    if malformed:
        with pytest.raises(ValueError, match="tax_unit_role_input"):
            simulation.calculate("is_tax_unit_head", YEAR)
    else:
        simulation.calculate("is_tax_unit_head", YEAR)
