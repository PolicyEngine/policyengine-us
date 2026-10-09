import functools

from policyengine_us.model_api import *
from policyengine_core.parameters import load_parameter_file
from policyengine_core.periods import instant

# Cal. Const. art. XIII, § 36(f)(2) (single, separate, and through RTC § 17045
# joint and surviving spouse) and § 36(f)(3) (head of household) apply the
# rates above 9.3% to taxable years before January 1, 2031. Proposition 3
# (2026), SEC. 4, strikes that end date, so the rates in effect for 2030 keep
# applying from 2031 onward.
LAST_PRE_SUNSET_YEAR = instant("2030-01-01")
SUNSET = instant("2031-01-01")
HORIZON_END = instant("2100-12-31")
FILING_STATUSES = [
    "single",
    "joint",
    "separate",
    "surviving_spouse",
    "head_of_household",
]


def _active_windows(in_effect) -> list:
    """Return the (start, stop) instants within SUNSET..HORIZON_END where the
    dated values of ``in_effect`` are true.

    ``values_list`` holds the user's dated overrides in reverse chronological
    order; each value applies from its instant until the next later one.
    """
    windows = []
    later_start = None
    for value_at_instant in in_effect.values_list:
        start = instant(value_at_instant.instant_str)
        if value_at_instant.value:
            window_start = max(start, SUNSET)
            window_stop = HORIZON_END
            if later_start is not None:
                window_stop = min(later_start.offset(-1, "day"), HORIZON_END)
            if window_start <= window_stop:
                windows.append((window_start, window_stop))
        later_start = start
    return sorted(windows)


@functools.lru_cache(maxsize=None)
def _enacted_schedule(file_path: str):
    # The schedule as enacted, read from the file the rates were loaded from,
    # so the reform can tell the statutory sunset apart from a user's edit.
    return load_parameter_file(file_path)


def _constant_intervals(start, stop, *parameters) -> list:
    """Split start..stop into the (start, stop) intervals on which every
    parameter keeps one value."""
    cuts = {start}
    for parameter in parameters:
        for value_at_instant in parameter.values_list:
            cut = instant(value_at_instant.instant_str)
            if start < cut <= stop:
                cuts.add(cut)
    cuts = sorted(cuts)
    stops = [cut.offset(-1, "day") for cut in cuts[1:]] + [stop]
    return list(zip(cuts, stops))


def _restore_pre_sunset_rates(rates, enacted_rates: dict, windows: list) -> None:
    """Within each window, give each bracket whose enacted rate the sunset
    changes its 2030 rate, wherever the enacted post-sunset rate applies.

    ``enacted_rates`` maps each filing status to its enacted schedule. Brackets
    the sunset leaves unchanged keep any edit, including one bounded to 2030,
    and so do intervals whose rate differs from the enacted rate, which a user
    has set explicitly. Restored intervals no longer match the enacted rate, so
    applying the reform again changes nothing.
    """
    updates = []
    for status in FILING_STATUSES:
        brackets = getattr(rates, status).brackets
        for bracket, enacted_bracket in zip(brackets, enacted_rates[status].brackets):
            rate = bracket.rate
            enacted_rate = enacted_bracket.rate
            if enacted_rate(SUNSET) == enacted_rate(LAST_PRE_SUNSET_YEAR):
                continue
            # The 2030 rate, including any rate the user set for 2030.
            pre_sunset_rate = rate(LAST_PRE_SUNSET_YEAR)
            for window_start, window_stop in windows:
                for start, stop in _constant_intervals(
                    window_start, window_stop, rate, enacted_rate
                ):
                    if rate(start) == enacted_rate(start):
                        updates.append((rate, start, stop, pre_sunset_rate))
    # Read every rate before writing any.
    for rate, start, stop, value in updates:
        rate.update(start=start, stop=stop, value=value)


def create_ca_prop3(respect_in_effect: bool = False) -> Reform:
    def modify_parameters(parameters):
        if respect_in_effect:
            windows = _active_windows(parameters.gov.contrib.states.ca.prop3.in_effect)
        else:
            windows = [(SUNSET, HORIZON_END)]
        rates = parameters.gov.states.ca.tax.income.rates
        enacted_rates = {
            status: _enacted_schedule(getattr(rates, status).file_path)
            for status in FILING_STATUSES
        }
        _restore_pre_sunset_rates(rates, enacted_rates, windows)
        return parameters

    class reform(Reform):
        def apply(self):
            self.modify_parameters(modify_parameters)

    return reform


def create_ca_prop3_reform(parameters, period, bypass: bool = False):
    # The bypass instance, used by YAML `reforms:` tests, restores the rates
    # for 2031-2100 regardless of in_effect. Otherwise the reform applies only
    # in the years from 2031 onward in which in_effect is true.
    if bypass:
        return create_ca_prop3()

    if _active_windows(parameters.gov.contrib.states.ca.prop3.in_effect):
        return create_ca_prop3(respect_in_effect=True)
    else:
        return None


ca_prop3 = create_ca_prop3_reform(None, None, bypass=True)
