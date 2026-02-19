from policyengine_us.model_api import *


class nj_unemployment_insurance_average_weekly_wage(Variable):
    value_type = float
    entity = Person
    label = "New Jersey unemployment insurance average weekly wage"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.nj.gov/labor/myunemployment/before/about/calculator/",
    )
    defined_for = StateCode.NJ

    def formula(person, period, parameters):
        base_wages = person(
            "nj_unemployment_insurance_base_period_wages", period
        )
        base_weeks = person(
            "nj_unemployment_insurance_base_period_weeks", period
        )
        return where(base_weeks > 0, base_wages / base_weeks, 0)
