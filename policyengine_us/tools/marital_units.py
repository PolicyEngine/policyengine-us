"""Construct missing household marital units without replacing supplied data."""

import numbers

import numpy as np
from policyengine_core import periods

# The age below which is_child treats a person as a child.
_ADULT_AGE = 18


class _LeaveToCore(Exception):
    """Malformed input that the situation builder reports more clearly."""


def _is_true(value):
    # Core reads real, NumPy and numeric booleans; leave strings and other
    # values to its validation.
    return isinstance(value, (bool, np.bool_, numbers.Number)) and bool(value)


def _true_input_periods(entity, variable, default_period, require_constant=False):
    values = entity.get(variable, {})
    if not isinstance(values, dict):
        values = {default_period: values}
    supplied = {key: value for key, value in values.items() if value is not None}
    if require_constant and len({_is_true(value) for value in supplied.values()}) > 1:
        raise ValueError(
            f"Cannot infer static marital units from changing {variable} inputs. "
            "Supply marital_units explicitly."
        )
    try:
        return {
            periods.period(key)
            for key, value in supplied.items()
            if key is not None and _is_true(value)
        }
    except ValueError as error:
        raise _LeaveToCore from error


def _periods_overlap(first, second):
    return any(a.contains(b) or b.contains(a) for a in first for b in second)


def _is_minor(person, default_period):
    values = person.get("age", {})
    if not isinstance(values, dict):
        values = {default_period: values}
    return any(
        isinstance(value, numbers.Number)
        and not isinstance(value, bool)
        and value < _ADULT_AGE
        for value in values.values()
    )


def _membership(situation, plural, people):
    groups = situation.get(plural)
    if groups is None:
        return {name: None for name in people}
    # Core assigns unlisted people their own group, including when the
    # caller supplies an empty mapping rather than omitting the entity.
    result = {name: ("singleton", name) for name in people}
    listed = set()
    for name, group in groups.items():
        members = group.get("members", [])
        if not isinstance(members, list):
            members = [members]
        for member in members:
            if str(member) in listed:
                raise _LeaveToCore
            listed.add(str(member))
            result[str(member)] = ("supplied", name)
    return result


def _married_family_pair(members, people, situation, families, default_period):
    """The two adults of a married family in this tax unit and household.

    A family's explicit ``is_married`` input says its adults are married.
    Pair them when exactly two of its adults, neither an explicit dependent
    nor separated, share this tax unit and household; otherwise leave them
    as singletons. Ages are read only to set aside children.
    """
    supplied_families = situation.get("families") or {}
    adults = {}
    for name in members:
        family = families[name]
        if family is None or family[0] != "supplied":
            continue
        if not _true_input_periods(
            supplied_families[family[1]], "is_married", default_period, True
        ):
            continue
        person = people[name]
        if (
            _is_minor(person, default_period)
            or _true_input_periods(person, "is_tax_unit_dependent", default_period)
            or _true_input_periods(person, "is_separated", default_period)
        ):
            continue
        adults.setdefault(family[1], []).append(name)
    couples = [names for names in adults.values() if len(names) == 2]
    return couples[0] if len(couples) == 1 else None


def infer_missing_marital_units(situation, default_period=None):
    """Pair only explicitly reported couples when marital units are omitted.

    Supplied membership, including an empty mapping, is authoritative. With
    no supplied membership, a couple is paired in two cases, both within
    one tax unit and household: an unambiguous pair of true head/spouse
    inputs for overlapping periods, or, without such a pair, the two adults
    of a family whose explicit ``is_married`` input is true. Other people
    receive singleton units, without claiming that their marital status is
    known. Calculated roles are never consulted, and ages only set children
    aside from a married family. Core calls this hook on a private copy
    before building populations; malformed input is left to its validation.
    """
    if situation.get("marital_units") is not None:
        return situation
    people = situation.get("people", {})
    # Leave malformed entity objects to the builder's standard validation.
    if not isinstance(people, dict) or any(
        not isinstance(person, dict) for person in people.values()
    ):
        return situation
    for plural in ("tax_units", "households", "families"):
        supplied = situation.get(plural)
        if supplied is not None and (
            not isinstance(supplied, dict)
            or any(not isinstance(group, dict) for group in supplied.values())
        ):
            return situation
    people = {str(name): person for name, person in people.items()}
    try:
        units = _infer_units(situation, people, default_period)
    except _LeaveToCore:
        return situation
    situation["marital_units"] = units
    return situation


def _infer_units(situation, people, default_period):
    tax_units = _membership(situation, "tax_units", people)
    households = _membership(situation, "households", people)
    families = _membership(situation, "families", people)
    groups = {}
    for name in people:
        groups.setdefault((tax_units[name], households[name]), []).append(name)

    units = {name: {"members": [name]} for name in people}
    for members in groups.values():
        pair = _explicit_role_pair(members, people, default_period)
        if pair is None:
            pair = _married_family_pair(
                members, people, situation, families, default_period
            )
        if pair is not None:
            first, second = pair
            units[first]["members"].append(second)
            del units[second]
    return units


def _explicit_role_pair(members, people, default_period):
    heads = {
        name: dates
        for name in members
        if (
            dates := _true_input_periods(
                people[name], "is_tax_unit_head", default_period
            )
        )
    }
    spouses = {
        name: dates
        for name in members
        if (
            dates := _true_input_periods(
                people[name], "is_tax_unit_spouse", default_period
            )
        )
    }
    if not heads or not spouses:
        return None
    if len(heads) != 1 or len(spouses) != 1 or heads.keys() == spouses.keys():
        raise ValueError(
            "Cannot infer an unambiguous head/spouse pair. "
            "Supply marital_units explicitly."
        )
    head = next(iter(heads))
    spouse = next(iter(spouses))
    if not _periods_overlap(heads[head], spouses[spouse]):
        return None
    _true_input_periods(people[head], "is_tax_unit_head", default_period, True)
    _true_input_periods(people[spouse], "is_tax_unit_spouse", default_period, True)
    for name in (head, spouse):
        if _true_input_periods(people[name], "is_tax_unit_dependent", default_period):
            raise ValueError(
                "Cannot infer a marital pair from an explicit dependent "
                "also marked as head or spouse. Supply marital_units explicitly."
            )
    if any(
        _true_input_periods(people[name], "is_separated", default_period)
        for name in (head, spouse)
    ):
        return None
    return head, spouse
