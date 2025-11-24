from policyengine_us.model_api import *


class mo_tanf_gross_earned_income(Variable):
    value_type = float
    entity = Person
    label = "Missouri TANF gross earned income"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/missouri/13-CSR-40-2-310",
        "https://dssmanuals.mo.gov/temporary-assistance-case-management/0210-015-05/",
    )
    defined_for = StateCode.MO

    def formula(person, period, parameters):
        # Use federal baseline for earned income sources
        employment_income = person("employment_income", period)
        self_employment_income = person("self_employment_income", period)

        # Total earned income per person
        return employment_income + self_employment_income
