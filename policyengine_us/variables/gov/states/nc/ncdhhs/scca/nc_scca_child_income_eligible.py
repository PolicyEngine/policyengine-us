from policyengine_us.model_api import *


class nc_scca_child_income_eligible(Variable):
    value_type = bool
    entity = Person
    label = "North Carolina Subsidized Child Care Assistance (SCCA) program child income eligibility"
    reference = "https://policies.ncdhhs.gov/wp-content/uploads/FINAL-Chapter-7-Family-definition-and-determining-income-eligibility-08-05-24.pdf#page=2"
    definition_period = MONTH
    defined_for = StateCode.NC

    def formula(person, period, parameters):
        # The family's countable income is compared to each child's own
        # age-based FPL limit, so siblings can have different outcomes.
        family_income = person.spm_unit("nc_scca_countable_income", period)
        rounded_family_income = np.round(family_income, 2)
        fpg = person.spm_unit("spm_unit_fpg", period)
        rate = person("nc_scca_fpg_rate", period.this_year)
        allowed_max_income = np.round(fpg * rate, 2)
        return rounded_family_income < allowed_max_income
