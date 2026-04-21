from policyengine_us.model_api import *


class sc_ccap_protective_services(Variable):
    value_type = bool
    entity = SPMUnit
    label = "South Carolina CCAP protective services category"
    definition_period = MONTH
    defined_for = StateCode.SC
    reference = (
        "https://www.scchildcare.org/media/ubhdm1at/1-13-2025_policy-manual.pdf#page=65",
        "https://www.scchildcare.org/media/ubhdm1at/1-13-2025_policy-manual.pdf#page=108",
    )

    def formula(spm_unit, period, parameters):
        has_foster_child = add(spm_unit, period, ["is_in_foster_care"]) > 0
        is_homeless = spm_unit.household("is_homeless", period.this_year)
        has_protective_child = (
            add(
                spm_unit,
                period.this_year,
                ["receives_or_needs_protective_services"],
            )
            > 0
        )
        return has_foster_child | is_homeless | has_protective_child
