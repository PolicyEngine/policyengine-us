from policyengine_us.model_api import *


class vt_ccfap_categorically_exempt(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    defined_for = StateCode.VT
    label = "Categorically exempt from Vermont CCFAP income test"
    reference = (
        "https://outside.vermont.gov/dept/DCF/Shared%20Documents/CDD/CCFAP/CCFAP-Regulations.pdf#page=11",
        "https://legislature.vermont.gov/statutes/section/33/035/03512",
    )

    def formula(spm_unit, period, parameters):
        # Reach Up (VT TANF) recipients — MONTH variable
        reach_up = spm_unit("is_tanf_enrolled", period)
        # Protective services — YEAR variable
        protective = (
            add(
                spm_unit,
                period.this_year,
                ["receives_or_needs_protective_services"],
            )
            > 0
        )
        # Foster care — MONTH variable
        foster = add(spm_unit, period, ["is_in_foster_care"]) > 0
        return reach_up | protective | foster
