"""Construct missing household marital units without replacing supplied data."""

import numbers

import numpy as np
from policyengine_core import periods

# The age below which is_child treats a person as a child.
_ADULT_AGE = 18


class _LeaveToCore(Exception):
    """Malformed input that the situation builder reports more clearly."""


# Supplied role inputs that settle a tax unit without a couple.
_NO_PAIR = object()


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


def _explicitly_unmarried(pair, situation, families):
    """Whether both adults share a family whose is_married inputs are all false."""
    first, second = (families[name] for name in pair)
    if first is None or first != second or first[0] != "supplied":
        return False
    values = (situation.get("families") or {})[first[1]].get("is_married")
    if values is None:
        return False
    if not isinstance(values, dict):
        values = {None: values}
    supplied = [value for value in values.values() if value is not None]
    return bool(supplied) and not any(_is_true(value) for value in supplied)


def infer_missing_marital_units(situation, default_period=None, system=None):
    """Pair likely couples when a situation omits marital units.

    Supplied membership, including an empty mapping, is authoritative, and
    datasets never reach this hook, so their marital units always stand.
    With no supplied membership, each tax unit and household pairs at most
    one couple, from the first of these that applies:

    1. an unambiguous pair of true ``is_tax_unit_head`` and
       ``is_tax_unit_spouse`` inputs for overlapping periods;
    2. the head and spouse of a complete ``tax_unit_role_input``;
    3. the two adults of a family whose explicit ``is_married`` input is
       true;
    4. otherwise, with the country ``system``, the head and spouse that
       ``is_tax_unit_head`` and ``is_tax_unit_spouse`` infer from age order
       when everyone has their own marital unit: the oldest adult, and the
       next-oldest adult who fails the qualifying child age test against
       them, with no couple when anyone in the unit is separated or a
       family says the two aren't married.

    Everyone else receives their own unit, without claiming that their
    marital status is known. Calculated values are never read: step 4 reads
    the same inputs and parameters the role formulas read, so the units it
    builds agree with the inferred tax roles. Core calls this hook on a
    private copy before building populations; malformed input is left to
    its validation.
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
        units = _infer_units(situation, people, default_period, system)
    except _LeaveToCore:
        return situation
    situation["marital_units"] = units
    return situation


def _infer_units(situation, people, default_period, system):
    tax_units = _membership(situation, "tax_units", people)
    households = _membership(situation, "households", people)
    families = _membership(situation, "families", people)
    groups = {}
    tax_unit_members = {}
    for name in people:
        groups.setdefault((tax_units[name], households[name]), []).append(name)
        tax_unit_members.setdefault(tax_units[name], []).append(name)

    units = {name: {"members": [name]} for name in people}
    for (tax_unit, _), members in groups.items():
        pair = _group_pair(
            members,
            tax_unit_members[tax_unit],
            people,
            situation,
            families,
            default_period,
            system,
        )
        if pair is not None:
            first, second = pair
            units[first]["members"].append(second)
            del units[second]
    return units


def _group_pair(
    members, unit_members, people, situation, families, default_period, system
):
    """The couple, if any, among the members of one tax unit and household."""
    heads = _true_role_inputs(members, people, "is_tax_unit_head", default_period)
    spouses = _true_role_inputs(members, people, "is_tax_unit_spouse", default_period)
    if heads and spouses:
        pair = _explicit_role_pair(heads, spouses, people, default_period)
        return None if pair is _NO_PAIR else pair
    pair = _supplied_role_pair(members, people)
    if pair is not None:
        return None if pair is _NO_PAIR else pair
    pair = _married_family_pair(members, people, situation, families, default_period)
    if pair is not None or system is None:
        return pair
    # The role formulas rank the whole tax unit, which can span households.
    heads = _true_role_inputs(unit_members, people, "is_tax_unit_head", default_period)
    spouses = _true_role_inputs(
        unit_members, people, "is_tax_unit_spouse", default_period
    )
    if len(heads) > 1 or len(spouses) > 1:
        return None
    pair = _tax_fallback_pair(
        unit_members,
        people,
        default_period,
        system,
        head=next(iter(heads), None),
        spouse=next(iter(spouses), None),
    )
    # Only a couple who share this household share a marital unit.
    if pair is None or not set(pair) <= set(members):
        return None
    if _explicitly_unmarried(pair, situation, families):
        return None
    return pair


def _true_role_inputs(members, people, variable, default_period):
    return {
        name: dates
        for name in members
        if (dates := _true_input_periods(people[name], variable, default_period))
    }


def _explicit_role_pair(heads, spouses, people, default_period):
    if len(heads) != 1 or len(spouses) != 1 or heads.keys() == spouses.keys():
        raise ValueError(
            "Cannot infer an unambiguous head/spouse pair. "
            "Supply marital_units explicitly."
        )
    head = next(iter(heads))
    spouse = next(iter(spouses))
    if not _periods_overlap(heads[head], spouses[spouse]):
        return _NO_PAIR
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
        return _NO_PAIR
    return head, spouse


def _role_name(value):
    # Enum inputs arrive as names ("HEAD"), values ("Head") or members.
    return str(getattr(value, "name", value)).split(".")[-1].upper()


def _supplied_role_pair(members, people):
    """The head and spouse of a tax unit whose every member has a role.

    is_tax_unit_head and is_tax_unit_spouse use tax_unit_role_input only when
    every member of the unit supplies one; a partial or malformed set is an
    error there, so it pairs no one here.
    """
    roles = {}
    for name in members:
        values = people[name].get("tax_unit_role_input")
        if values is None:
            continue
        if not isinstance(values, dict):
            values = {None: values}
        supplied = {
            _role_name(value)
            for value in values.values()
            if value is not None and _role_name(value) != "UNSPECIFIED"
        }
        if len(supplied) > 1:
            raise ValueError(
                "Cannot infer static marital units from changing "
                "tax_unit_role_input inputs. Supply marital_units explicitly."
            )
        if supplied:
            roles[name] = supplied.pop()
    if not roles:
        return None
    heads = [name for name, role in roles.items() if role == "HEAD"]
    spouses = [name for name, role in roles.items() if role == "SPOUSE"]
    if len(roles) < len(members) or len(heads) != 1 or len(spouses) != 1:
        return _NO_PAIR
    return heads[0], spouses[0]


# Inputs the role formulas read for the age-order fallback.
_FALLBACK_INPUTS = (
    "age",
    "is_tax_unit_dependent",
    "is_separated",
    "is_full_time_student",
    "is_full_time_college_student",
    "is_in_k12_school",
    "is_permanently_and_totally_disabled",
)


def _dated_values(person, variable, default_period):
    """A person's supplied values of an input as (start, value), oldest first.

    An undated value with no default period has no start and applies to
    every year.
    """
    values = person.get(variable)
    if values is None:
        return []
    if not isinstance(values, dict):
        values = {default_period: values}
    undated = []
    dated = []
    for key, value in values.items():
        if value is None:
            continue
        if key is None:
            undated.append((None, value))
            continue
        try:
            start = periods.period(key).start
        except ValueError as error:
            raise _LeaveToCore from error
        dated.append((start, value))
    return undated + sorted(dated, key=lambda item: item[0])


def _fallback_years(members, people, default_period):
    years = set()
    if default_period is not None:
        try:
            years.add(periods.period(default_period).start.year)
        except ValueError as error:
            raise _LeaveToCore from error
    for name in members:
        for variable in _FALLBACK_INPUTS:
            for start, _ in _dated_values(people[name], variable, default_period):
                if start is not None:
                    years.add(start.year)
    return sorted(years)


def _value_in_year(person, variable, year, default_period, default, carries):
    """The input value the year's calculation reads.

    Core carries an input of a variable without a formula forward to later
    years; a variable with a formula computes years without an input.
    """
    value = default
    for start, supplied in _dated_values(person, variable, default_period):
        if start is None or start.year == year or (carries and start.year < year):
            value = supplied
    return value


def _tax_fallback_pair(members, people, default_period, system, head, spouse):
    """The couple is_tax_unit_head and is_tax_unit_spouse infer from age order.

    A pairing that changes between years can't be one static membership, so
    the unit pairs no one unless every year's inputs give the same couple.
    """
    years = _fallback_years(members, people, default_period)
    if not years:
        # No year to read the dependent age limits for.
        return None
    pairs = {
        _fallback_pair_in_year(
            members, people, year, default_period, system, head, spouse
        )
        for year in years
    }
    return pairs.pop() if len(pairs) == 1 else None


def _oldest(names, ages):
    # Ties go to the person listed first.
    return max(names, key=lambda name: ages[name]) if names else None


def _fallback_pair_in_year(members, people, year, default_period, system, head, spouse):
    def value(name, variable, default=False):
        carries = not system.get_variable(variable).formulas
        return _value_in_year(
            people[name], variable, year, default_period, default, carries
        )

    ages = {}
    for name in members:
        age = value(name, "age", system.get_variable("age").default_value)
        if not isinstance(age, numbers.Number) or isinstance(age, bool):
            raise _LeaveToCore
        ages[name] = age
    # head_or_spouse_candidates: adults, skipping input dependents unless
    # every adult is one.
    adults = [name for name in members if ages[name] >= _ADULT_AGE]
    candidates = [
        name for name in adults if not _is_true(value(name, "is_tax_unit_dependent"))
    ] or adults
    if head is None:
        head = _oldest([name for name in candidates if name != spouse], ages)
        if head is None:
            return None
    if spouse is not None:
        return head, spouse
    # is_tax_unit_spouse infers no spouse in a unit with a separated member.
    if any(_is_true(value(name, "is_separated")) for name in members):
        return None
    # The qualifying child age test (26 USC 152(c)(3)), as is_tax_unit_spouse
    # applies it to adults outside the head's marital unit. A reform delegates
    # this hook to its baseline, so these are the baseline's age limits.
    limits = system.parameters(f"{year}-01-01").gov.irs.dependent.ineligible_age

    def meets_age_test(name):
        student = value(name, "is_full_time_student", None)
        if student is None:
            # is_full_time_student's formula: college or K-12 enrolment.
            student = _is_true(value(name, "is_full_time_college_student")) or (
                _is_true(value(name, "is_in_k12_school"))
            )
        limit = limits.student if _is_true(student) else limits.non_student
        return (ages[name] < limit and ages[name] < ages[head]) or _is_true(
            value(name, "is_permanently_and_totally_disabled")
        )

    spouse = _oldest(
        [name for name in candidates if name != head and not meets_age_test(name)],
        ages,
    )
    return None if spouse is None else (head, spouse)
