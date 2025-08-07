from policyengine_us.model_api import *


class nc_scca_entry_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "North Carolina entry income eligibility for Subsidized Child Care Assistance program"
    reference = "https://policies.ncdhhs.gov/wp-content/uploads/chapter-8-parental-fees-7.pdf#page=8"
    definition_period = MONTH
    defined_for = StateCode.NC

    def formula(spm_unit, period, parameters):
        family_total_income = spm_unit("nc_scca_countable_income", period)
        rounded_family_total_income = np.round(family_total_income, 2)

        fpg = spm_unit("spm_unit_fpg", period)

        rate = spm_unit("nc_scca_fpg_rate", period.this_year)

        allowed_max_income = np.round(fpg * rate, 2)

        return rounded_family_total_income < allowed_max_income
