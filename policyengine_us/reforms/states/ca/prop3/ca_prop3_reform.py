from policyengine_us.model_api import *
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


def create_ca_prop3(respect_in_effect: bool = False) -> Reform:
    def modify_parameters(parameters):
        if respect_in_effect:
            windows = _active_windows(parameters.gov.contrib.states.ca.prop3.in_effect)
        else:
            windows = [(SUNSET, HORIZON_END)]
        rates = parameters.gov.states.ca.tax.income.rates
        # Snapshot every bracket's 2030 and 2031 rates before modifying any,
        # so each window restores the pre-sunset rate, including any rate the
        # user set for 2030.
        restorations = []
        for status in FILING_STATUSES:
            for bracket in getattr(rates, status).brackets:
                pre_sunset_rate = bracket.rate(LAST_PRE_SUNSET_YEAR)
                if bracket.rate(SUNSET) != pre_sunset_rate:
                    restorations.append((bracket.rate, pre_sunset_rate))
        for rate, pre_sunset_rate in restorations:
            for start, stop in windows:
                rate.update(start=start, stop=stop, value=pre_sunset_rate)
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
