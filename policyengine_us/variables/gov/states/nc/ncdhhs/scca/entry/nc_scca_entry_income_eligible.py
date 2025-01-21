from policyengine_us.model_api import *


class nc_scca_entry_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Income has to be eligible for the entry of North Carolina Subsidized Child Care Assistance program"
    reference = "https://ncchildcare.ncdhhs.gov/Portals/0/documents/pdf/A/ACF-118_CCDF_FFY_2022-2024_For_North_Carolina_Amendment_1.pdf?ver=C9YfIUPAFekeBA3I1mN8aA%3d%3d#page=83"
    definition_period = MONTH
    defined_for = StateCode.NC

    def formula(spm_unit, period, parameters):        
        family_total_income = spm_unit('nc_scca_countable_income', period)

        fpg = spm_unit("spm_unit_fpg", period)

        rate = spm_unit("nc_scca_fpl_rate", period)

        allowed_max_income = fpg * rate

        income_eligible = family_total_income < allowed_max_income

        return income_eligible
