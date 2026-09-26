from policyengine_us.model_api import *
from policyengine_core.periods import period as period_
from policyengine_core.periods import instant

# Under Cal. Const. art. XIII, § 36(f)(2), the 10.3%, 11.3% and 12.3% rates apply
# to taxable years before January 1, 2031. Proposition 3 (2026) would make them
# permanent, so the three brackets above 9.3% keep these rates from 2031 onward.
TOP_BRACKET_RATES = {6: 0.103, 7: 0.113, 8: 0.123}
FILING_STATUSES = [
    "single",
    "joint",
    "separate",
    "surviving_spouse",
    "head_of_household",
]


def create_ca_prop3() -> Reform:
    def modify_parameters(parameters):
        rates = parameters.gov.states.ca.tax.income.rates
        for status in FILING_STATUSES:
            schedule = getattr(rates, status)
            for bracket, rate in TOP_BRACKET_RATES.items():
                schedule.brackets[bracket].rate.update(
                    start=instant("2031-01-01"),
                    stop=instant("2100-12-31"),
                    value=rate,
                )
        return parameters

    class reform(Reform):
        def apply(self):
            self.modify_parameters(modify_parameters)

    return reform


def create_ca_prop3_reform(parameters, period, bypass: bool = False):
    if bypass:
        return create_ca_prop3()

    p = parameters.gov.contrib.states.ca.prop3

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_ca_prop3()
    else:
        return None


ca_prop3 = create_ca_prop3_reform(None, None, bypass=True)
