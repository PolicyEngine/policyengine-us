"""Properties of supplied tax-unit roles and filing statuses over generated units.

Invariants, each checked for every generated household:

1. Partition: every person is exactly one of head, spouse and dependent.
2. Supplied roles hold: in a unit whose roles are supplied, the role variables
   equal the supplied roles, so the unit has exactly one head and at most one
   spouse.
3. Fallback: in a unit without supplied roles, the roles equal an independent
   implementation of age ordering (the oldest adult heads the unit, earliest
   member on ties; the next-oldest adult is the spouse unless any member is
   separated).
4. Supplied statuses hold: a supplied filing status is the filing status, and a
   supplied unit files jointly exactly when it has a spouse.
5. Workaround equivalence (differential): supplying roles and statuses through
   the input variables gives the same filing status and income tax as setting
   is_tax_unit_head, is_tax_unit_spouse, is_tax_unit_dependent and
   filing_status directly, the policyengine-taxsim workaround. The explicit pin
   must cover every unit: a situation that sets filing_status for some tax
   units gives the rest the default (SINGLE) rather than the formula.
6. Switch-off locality: abolishing one status's eligibility rule re-derives the
   units supplied with that status and no others.
7. Error contract: supplied roles raise exactly when malformed - supplied for
   only some members, or not exactly one HEAD and at most one SPOUSE.
"""

from functools import cache

from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st
import numpy as np
import pytest

from policyengine_core.reforms import Reform

from policyengine_us import CountryTaxBenefitSystem, Simulation

YEAR = 2024
STATUSES = ["SINGLE", "SEPARATE", "HEAD_OF_HOUSEHOLD", "SURVIVING_SPOUSE"]
SETTINGS = dict(
    derandomize=True,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)


@st.composite
def tax_units(draw, supplied=None, every_status=False, status=None):
    """One tax unit; ``status`` forces a supplied unit with that non-joint status."""
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
    forced = status
    with_roles = forced is not None or (
        draw(st.booleans()) if supplied is None else supplied
    )
    roles = None
    status = None
    if with_roles:
        head = draw(st.integers(0, size - 1))
        others = [i for i in range(size) if i != head]
        spouse = None
        if others and forced is None:
            spouse = draw(st.one_of(st.none(), st.sampled_from(others)))
        roles = ["DEPENDENT"] * size
        roles[head] = "HEAD"
        if spouse is not None:
            roles[spouse] = "SPOUSE"
        if forced is not None:
            status = forced
        elif every_status or draw(st.booleans()):
            status = "JOINT" if spouse is not None else draw(st.sampled_from(STATUSES))
    return dict(
        ages=ages,
        separated=separated,
        earnings=earnings,
        roles=roles,
        status=status,
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
            people[name] = person
            members.append(name)
        group = {"members": members}
        if unit["status"]:
            key = "filing_status" if pin_explicitly else "filing_status_input"
            group[key] = {YEAR: unit["status"]}
        tax_unit_groups[f"u{u}"] = group
    return {
        "people": people,
        "tax_units": tax_unit_groups,
        "households": {
            "household": {"members": list(people), "state_name": {YEAR: "TX"}}
        },
    }


def _age_rule(ages, separated):
    # Mirrors the fallback as it stands, including its unit-wide separation
    # gate: any separated member blocks every spouse. That gate is a known
    # defect (#9620); update this reference when it is fixed.
    adults = [i for i, age in enumerate(ages) if age >= 18]
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


@cache
def _abolished(rule):
    """A system with one eligibility rule abolished, built once per rule."""
    reform = Reform.from_dict(
        {f"gov.abolitions.{rule}": {"2000-01-01.2100-12-31": True}},
        country_id="us",
    )
    return CountryTaxBenefitSystem(reform=reform)


@settings(max_examples=40, **SETTINGS)
@given(st.lists(tax_units(), min_size=1, max_size=4))
def test_roles_and_statuses_follow_supplied_values_and_otherwise_rules(units):
    simulation = Simulation(situation=_situation(units))
    head = simulation.calculate("is_tax_unit_head", YEAR).astype(bool)
    spouse = simulation.calculate("is_tax_unit_spouse", YEAR).astype(bool)
    dependent = simulation.calculate("is_tax_unit_dependent", YEAR).astype(bool)
    status = simulation.calculate("filing_status", YEAR).decode_to_str().tolist()
    # 1. Partition.
    assert np.all(head.astype(int) + spouse.astype(int) + dependent.astype(int) == 1)
    for unit, h, s, unit_status in zip(
        units, _by_unit(units, head), _by_unit(units, spouse), status
    ):
        if unit["roles"]:
            # 2. Supplied roles hold.
            assert h == [role == "HEAD" for role in unit["roles"]]
            assert s == [role == "SPOUSE" for role in unit["roles"]]
            # 4. Supplied units file jointly exactly when they have a spouse.
            assert (unit_status == "JOINT") == any(s)
        else:
            # 3. Fallback equals the independent age-ordering rule.
            expected_head, expected_spouse = _age_rule(unit["ages"], unit["separated"])
            assert h == [i == expected_head for i in range(len(h))]
            assert s == [i == expected_spouse for i in range(len(s))]
        if unit["status"]:
            # 4. A supplied status is the status.
            assert unit_status == unit["status"]


@settings(max_examples=15, **SETTINGS)
@given(st.lists(tax_units(supplied=True, every_status=True), min_size=1, max_size=3))
def test_supplied_inputs_match_the_explicit_pin(units):
    # 5. Differential: input variables and a complete explicit pin agree.
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


@pytest.mark.parametrize(
    "rule,status",
    [
        ("head_of_household_eligible", "HEAD_OF_HOUSEHOLD"),
        ("surviving_spouse_eligible", "SURVIVING_SPOUSE"),
    ],
)
@settings(max_examples=15, **SETTINGS)
@given(data=st.data())
def test_abolishing_a_rule_moves_only_units_supplied_with_its_status(
    rule, status, data
):
    # Every example holds at least one unit supplied with the target status,
    # beside other supplied units.
    target = data.draw(tax_units(status=status), label="target")
    others = data.draw(
        st.lists(tax_units(supplied=True, every_status=True), max_size=2),
        label="others",
    )
    position = data.draw(st.integers(0, len(others)), label="position")
    units = others[:position] + [target] + others[position:]
    assert sum(unit["status"] == status for unit in units) >= 1
    simulation = Simulation(
        situation=_situation(units), tax_benefit_system=_abolished(rule)
    )
    results = simulation.calculate("filing_status", YEAR).decode_to_str().tolist()
    for unit, result in zip(units, results):
        # 6. Switch-off locality.
        if unit["status"] == status:
            assert result != status
        elif unit["status"]:
            assert result == unit["status"]


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
    # 7. Error contract.
    simulation = Simulation(situation=situation)
    if malformed:
        with pytest.raises(ValueError, match="tax_unit_role_input"):
            simulation.calculate("is_tax_unit_head", YEAR)
    else:
        simulation.calculate("is_tax_unit_head", YEAR)
