"""Construct missing household marital units without replacing supplied data."""

from policyengine_core import periods


def _true_input_periods(person, variable, default_period, require_constant=False):
    values = person.get(variable, {})
    if not isinstance(values, dict):
        values = {default_period: values}
    supplied = {key: value for key, value in values.items() if value is not None}
    if require_constant and True in supplied.values() and False in supplied.values():
        raise ValueError(
            f"Cannot infer static marital units from changing {variable} inputs. "
            "Supply marital_units explicitly."
        )
    return {
        periods.period(key)
        for key, value in supplied.items()
        if value is True and key is not None
    }


def _membership(situation, plural, people):
    groups = situation.get(plural)
    if groups is None:
        return {name: None for name in people}
    # Core assigns unlisted people their own group, including when the
    # caller supplies an empty mapping rather than omitting the entity.
    result = {name: ("singleton", name) for name in people}
    for name, group in groups.items():
        members = group.get("members", [])
        if not isinstance(members, list):
            members = [members]
        for member in members:
            result[str(member)] = ("supplied", name)
    return result


def infer_missing_marital_units(situation, default_period=None):
    """Use only explicit head/spouse pairs when marital units are omitted.

    Supplied membership, including an empty mapping, is authoritative. With
    no supplied membership, an unambiguous pair must have true head/spouse
    inputs for a common period and share both a tax unit and a household.
    Other people receive singleton units, without claiming that their
    marital status is known. Calculated roles and ages are never consulted.
    Core calls this hook on a private copy before building populations.
    """
    if situation.get("marital_units") is not None:
        return situation
    people = situation.get("people", {})
    # Leave malformed entity objects to the builder's standard validation.
    if not isinstance(people, dict) or any(
        not isinstance(person, dict) for person in people.values()
    ):
        return situation
    for plural in ("tax_units", "households"):
        supplied = situation.get(plural)
        if supplied is not None and (
            not isinstance(supplied, dict)
            or any(not isinstance(group, dict) for group in supplied.values())
        ):
            return situation
    people = {str(name): person for name, person in people.items()}
    tax_units = _membership(situation, "tax_units", people)
    households = _membership(situation, "households", people)
    groups = {}
    for name in people:
        groups.setdefault((tax_units[name], households[name]), []).append(name)

    units = {name: {"members": [name]} for name in people}
    for members in groups.values():
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
            continue
        if len(heads) != 1 or len(spouses) != 1 or heads.keys() == spouses.keys():
            raise ValueError(
                "Cannot infer an unambiguous head/spouse pair. "
                "Supply marital_units explicitly."
            )
        head = next(iter(heads))
        spouse = next(iter(spouses))
        if not heads[head] & spouses[spouse]:
            continue
        _true_input_periods(people[head], "is_tax_unit_head", default_period, True)
        _true_input_periods(people[spouse], "is_tax_unit_spouse", default_period, True)
        for name in (head, spouse):
            if _true_input_periods(
                people[name], "is_tax_unit_dependent", default_period
            ):
                raise ValueError(
                    "Cannot infer a marital pair from an explicit dependent "
                    "also marked as head or spouse. Supply marital_units explicitly."
                )
        if any(
            _true_input_periods(people[name], "is_separated", default_period)
            for name in (head, spouse)
        ):
            continue
        units[head]["members"].append(spouse)
        del units[spouse]

    situation["marital_units"] = units
    return situation
