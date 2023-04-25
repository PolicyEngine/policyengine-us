from policyengine_core.model_api import *
from policyengine_core import periods


def str_to_instant(s):
    return periods.Instant(tuple(map(lambda s: int(s), s.split("-"))))


def backdate_parameters(
    root: str = None, first_instant: str = "2021-01-01"
) -> Reform:
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
