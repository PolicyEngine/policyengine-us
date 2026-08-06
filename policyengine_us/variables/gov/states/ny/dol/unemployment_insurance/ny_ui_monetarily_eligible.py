from policyengine_us.model_api import *


class ny_ui_monetarily_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Monetarily eligible for New York unemployment insurance"
    definition_period = YEAR
    reference = "https://www.nysenate.gov/legislation/laws/LAB/527"
    defined_for = StateCode.NY

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ny.dol.unemployment_insurance
        high_quarter_wages = person("ny_ui_high_quarter_wages", period)
        base_period_wages = person("ny_ui_base_period_wages", period)
        quarters_with_wages = person("ny_ui_quarters_with_wages", period)

        meets_high_quarter_minimum = (
            high_quarter_wages >= p.eligibility.high_quarter_minimum
        )
        meets_quarters_test = quarters_with_wages >= p.eligibility.quarters_required
        meets_standard_wages_test = (
            base_period_wages
            >= p.eligibility.base_wages_multiplier * high_quarter_wages
        )
        other_quarters_wages = base_period_wages - high_quarter_wages
        meets_capped_wages_test = other_quarters_wages >= (
            p.eligibility.capped_other_quarters_rate * p.eligibility.high_quarter_cap
        )
        meets_wages_test = where(
            high_quarter_wages >= p.eligibility.high_quarter_cap,
            meets_capped_wages_test,
            meets_standard_wages_test,
        )
        return meets_high_quarter_minimum & meets_quarters_test & meets_wages_test
