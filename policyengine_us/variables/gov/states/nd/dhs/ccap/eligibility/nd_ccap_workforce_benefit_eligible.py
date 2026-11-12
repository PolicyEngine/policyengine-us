from policyengine_us.model_api import *


class nd_ccap_workforce_benefit_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "North Dakota CCAP family meets the Workforce Benefit employment test"
    defined_for = StateCode.ND
    reference = "https://www.nd.gov/dhs/policymanuals/40028/Content/400_28_20_40.htm"

    def formula_2024_06_01(spm_unit, period, parameters):
        return spm_unit.any(
            spm_unit.members("nd_ccap_workforce_benefit_eligible_parent", period)
        )
