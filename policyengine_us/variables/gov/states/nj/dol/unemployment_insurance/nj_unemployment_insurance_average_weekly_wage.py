from policyengine_us.model_api import *


class nj_unemployment_insurance_average_weekly_wage(Variable):
    value_type = float
    entity = Person
    label = "New Jersey unemployment insurance average weekly wage"
    unit = USD
    documentation = "Average weekly wage during the base period, calculated as total base period wages divided by the number of base period weeks worked."
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

        # Avoid division by zero using where()
        return where(base_weeks > 0, base_wages / base_weeks, 0)
