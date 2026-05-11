from policyengine_us.model_api import *


class ny_tanf_need_standard(Variable):
    value_type = float
    entity = SPMUnit
    label = "New York TANF need standard"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.NY
    reference = "https://www.law.cornell.edu/regulations/new-york/18-NYCRR-352.1"

    def formula(spm_unit, period, parameters):
        # Per 18 NYCRR 352.1: Standard of need = basic monthly allowance
        # + home energy allowance + supplemental home energy allowance
        # + shelter allowance (capped at the local agency maximum).
        return add(
            spm_unit,
            period,
            [
                "ny_tanf_basic_monthly_allowance",
                "ny_tanf_home_energy_allowance",
                "ny_tanf_supplemental_home_energy_allowance",
                "ny_tanf_shelter_allowance",
            ],
        )
