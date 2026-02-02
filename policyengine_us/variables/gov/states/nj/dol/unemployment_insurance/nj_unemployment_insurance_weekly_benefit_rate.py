from policyengine_us.model_api import *


class nj_unemployment_insurance_weekly_benefit_rate(Variable):
    value_type = float
    entity = Person
    label = "New Jersey unemployment insurance weekly benefit rate"
    unit = USD
    documentation = "Weekly benefit rate for New Jersey unemployment insurance, calculated as 60% of average weekly wage, capped at the maximum weekly benefit."
    definition_period = YEAR
    reference = (
        "https://www.nj.gov/labor/myunemployment/before/about/calculator/",
    )
    defined_for = StateCode.NJ

    def formula(person, period, parameters):
        average_weekly_wage = person(
            "nj_unemployment_insurance_average_weekly_wage", period
        )

        # Get parameters
        p = parameters(period).gov.states.nj.dol.unemployment_insurance
        wbr_rate = p.wbr_rate
        max_weekly_benefit = p.max_weekly_benefit

        # Calculate WBR: 60% of average weekly wage, capped at maximum
        calculated_wbr = average_weekly_wage * wbr_rate

        return min_(calculated_wbr, max_weekly_benefit)
