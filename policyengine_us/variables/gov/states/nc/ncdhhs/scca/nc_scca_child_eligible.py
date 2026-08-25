from policyengine_us.model_api import *


class nc_scca_child_eligible(Variable):
    value_type = bool
    entity = Person
    label = "North Carolina Subsidized Child Care Assistance (SCCA) program child eligibility"
    reference = "https://policies.ncdhhs.gov/wp-content/uploads/FINAL-Chapter-7-Family-definition-and-determining-income-eligibility-08-05-24.pdf#page=2"
    definition_period = MONTH
    defined_for = StateCode.NC

    def formula(person, period, parameters):
        age_eligible = person("nc_scca_child_age_eligible", period.this_year)
        income_eligible = person("nc_scca_child_income_eligible", period)
        return age_eligible & income_eligible
