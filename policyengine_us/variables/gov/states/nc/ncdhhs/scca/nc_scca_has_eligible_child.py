from policyengine_us.model_api import *


class nc_scca_has_eligible_child(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Any eligible child for North Carolina Subsidized Child Care Assistance program"
    definition_period = YEAR
    defined_for = StateCode.NC
    reference = "https://ncchildcare.ncdhhs.gov/Portals/0/documents/pdf/A/ACF-118_CCDF_FFY_2022-2024_For_North_Carolina_Amendment_1.pdf?ver=C9YfIUPAFekeBA3I1mN8aA%3d%3d#page=83"

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        is_any_child_age_eligible = person(
            "nc_scca_child_age_eligible", period
        )

        return spm_unit.any(is_any_child_age_eligible)
