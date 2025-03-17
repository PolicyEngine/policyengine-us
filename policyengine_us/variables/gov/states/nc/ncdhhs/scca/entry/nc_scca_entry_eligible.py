from policyengine_us.model_api import *


class nc_scca_entry_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "North Carolina entry eligibility for Subsidized Child Care Assistance Program"
    reference = "https://ncchildcare.ncdhhs.gov/Portals/0/documents/pdf/A/ACF-118_CCDF_FFY_2022-2024_For_North_Carolina_Amendment_1.pdf?ver=C9YfIUPAFekeBA3I1mN8aA%3d%3d#page=83"
    definition_period = MONTH
    defined_for = StateCode.NC

    def formula(spm_unit, period, parameters):
        income_eligible = spm_unit("nc_scca_entry_income_eligible", period)
        has_eligible_children = spm_unit("nc_scca_has_eligible_child", period)

        return income_eligible & has_eligible_children
