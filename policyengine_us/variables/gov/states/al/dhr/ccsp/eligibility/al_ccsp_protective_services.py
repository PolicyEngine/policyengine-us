from policyengine_us.model_api import *


class al_ccsp_protective_services(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Alabama CCSP protective services category"
    definition_period = MONTH
    defined_for = StateCode.AL
    reference = (
        "Alabama CCDF State Plan 2025-2027, Section 2.2.2(f)",
        "https://dhr.alabama.gov/wp-content/uploads/2023/04/2025-2027-CCDF-State-Plan-with-Approval-Letter.pdf#page=23",
    )

    def formula(spm_unit, period, parameters):
        # Foster care and homelessness are the modeled protective-service
        # categories. Kinship is excluded per §2.2.2(f). EHS-CCP,
        # child-welfare engagement, and TANF-Other Relative are not
        # tracked at the moment and are documented as limitations.
        has_foster_child = add(spm_unit, period, ["is_in_foster_care"]) > 0
        is_homeless = spm_unit.household("is_homeless", period.this_year)
        return has_foster_child | is_homeless
