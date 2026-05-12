from policyengine_us.model_api import *


class ok_ui_weekly_benefit_rate(Variable):
    value_type = float
    entity = Person
    label = "Oklahoma UI weekly benefit rate"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.OK
    reference = (
        "https://www.oklegislature.gov/OK_Statutes/CompleteTitles/os40.pdf#page=49"
    )

    def formula(person, period, parameters):
        # § 2-104(A): WBA = floor(high quarter taxable wages / divisor),
        # clamped to the statutory minimum and the annual maximum set under
        # § 2-104(B). § 2-102 specifies that fractional results are rounded
        # down to the next lower whole dollar.
        p = parameters(period).gov.states.ok.oesc.unemployment_insurance.wba
        high_quarter_taxable_wages = person("ok_ui_high_quarter_taxable_wages", period)
        raw_weekly_benefit_rate = np.floor(high_quarter_taxable_wages / p.divisor)
        return min_(max_(raw_weekly_benefit_rate, p.min_amount), p.max_amount)
