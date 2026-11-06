from policyengine_core.model_api import *
from policyengine_core import periods

# The earliest year the model computes. CountryTaxBenefitSystem backdates every
# parameter to the start of this year and no further, so a parameter first
# dated later has no value for an earlier period. A formula that reads an
# earlier period (for example, income from a prior year) must not reach before
# this year.
FIRST_MODELED_YEAR = 2015


def str_to_instant(s):
    return periods.Instant(tuple(map(lambda s: int(s), s.split("-"))))


def add_to_list_parameter(parameter, names) -> None:
    """Add variable names to every dated value of a list parameter.

    A reform that pays a new benefit or credit calls this in its
    ``modify_parameters`` to add its variable to an aggregate's list, such as
    ``gov.household.spm_unit_benefits``. Every baseline member stays in the
    list in every period, so the reform does not redefine the aggregate, and a
    program the baseline list gains later reaches the reform too.

    The names follow the existing members, in the order given. A name already
    in the list for a period is not added again for that period, so a reform
    applied twice, or two reforms that add the same variable, count it once.
    """
    names = list(dict.fromkeys(names))
    # values_list runs newest first. Each value lasts until the day before the
    # next newer value starts; the newest has no end.
    newer_start = None
    for value_at_instant in list(parameter.values_list):
        members = value_at_instant.value
        if members is not None:
            missing = [name for name in names if name not in members]
            if missing:
                parameter.update(
                    start=value_at_instant.instant_str,
                    stop=(
                        None
                        if newer_start is None
                        else str_to_instant(newer_start).offset(-1, "day")
                    ),
                    value=list(members) + missing,
                )
        newer_start = value_at_instant.instant_str


def backdate_parameters(root: str = None, first_instant: str = "2021-01-01") -> Reform:
    first_instant = str_to_instant(first_instant)
    node = root
    for param in node.get_descendants():
        if hasattr(param, "values_list"):
            earliest = param.values_list[-1]
            earliest_value = earliest.value
            earliest_instant = str_to_instant(earliest.instant_str)
            if first_instant < earliest_instant:
                num_days = (earliest_instant.date - first_instant.date).days
                param.update(
                    period=periods.Period(("day", first_instant, num_days)),
                    value=earliest_value,
                )
    return root
