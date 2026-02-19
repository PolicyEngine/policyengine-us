from policyengine_us.model_api import *


class nj_unemployment_insurance_weekly_benefit_rate(Variable):
    value_type = float
    entity = Person
    label = "New Jersey unemployment insurance weekly benefit rate"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.nj.gov/labor/myunemployment/before/about/calculator/",
    )
    defined_for = StateCode.NJ

    def formula(person, period, parameters):
        average_weekly_wage = person(
            "nj_unemployment_insurance_average_weekly_wage", period
        )
        p = parameters(period).gov.states.nj.dol.unemployment_insurance
        return min_(average_weekly_wage * p.wbr_rate, p.max_weekly_benefit)
