"""Test reforms that override the Alabama state unemployment rate parameter.

These reforms exist solely to drive `al_ui_max_weeks.yaml` boundary tests
through each rung of the duration-by-unemployment-rate bracket in
§ 25-4-74(a). Each reform pins the `state_unemployment_rate` parameter to a
fixed value so the bracket lookup deterministically returns the expected
number of weeks regardless of the FRED ALUR time series.
"""

from policyengine_core.model_api import *
from policyengine_core.periods import instant


def _make_reform(value):
    """Return a Reform subclass that pins state_unemployment_rate to ``value``."""

    def modify_parameters(parameters):
        parameters.gov.states.al.dol.unemployment_insurance.state_unemployment_rate.update(
            start=instant("2020-01-01"),
            stop=instant("2030-12-31"),
            value=value,
        )
        return parameters

    class _R(Reform):
        def apply(self):
            self.modify_parameters(modify_parameters)

    return _R


# Exactly 6.5% — boundary of the first bracket; expect 14 weeks.
set_state_unemployment_rate_to_6_5pct = _make_reform(0.065)

# 7.0% — boundary of the second bracket; expect 15 weeks.
set_state_unemployment_rate_to_7pct = _make_reform(0.07)

# 7.5% — boundary of the third bracket; expect 16 weeks.
set_state_unemployment_rate_to_7_5pct = _make_reform(0.075)

# 8.0% — boundary of the fourth bracket; expect 17 weeks.
set_state_unemployment_rate_to_8pct = _make_reform(0.08)

# 8.5% — boundary of the fifth bracket; expect 18 weeks.
set_state_unemployment_rate_to_8_5pct = _make_reform(0.085)

# 9.0% — boundary of the sixth bracket; expect 19 weeks.
set_state_unemployment_rate_to_9pct = _make_reform(0.09)

# 9.5% — boundary of the seventh (cap) bracket; expect 20 weeks.
set_state_unemployment_rate_to_9_5pct = _make_reform(0.095)

# 12% — well above the cap; expect 20 weeks.
set_state_unemployment_rate_to_12pct = _make_reform(0.12)

# 6.51% — just above the 6.5% boundary; expect 15 weeks (statute: > 6.5%).
set_state_unemployment_rate_to_6_51pct = _make_reform(0.0651)

# 15% — very high (well above 9.5% cap); expect 20 weeks.
set_state_unemployment_rate_to_15pct = _make_reform(0.15)
