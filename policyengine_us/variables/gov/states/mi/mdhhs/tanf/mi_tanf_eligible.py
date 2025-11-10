from policyengine_us.model_api import *


class mi_tanf_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Michigan FIP (TANF)"
    definition_period = MONTH
    reference = (
        "https://www.michigan.gov/mdhhs/-/media/Project/Websites/mdhhs/Inside-MDHHS/Reports-and-Statistics---Human-Services/State-Plans-and-Federal-Regulations/TANF_State_Plan_2023.pdf",
        "https://mdhhs-pres-prod.michigan.gov/olmweb/ex/bp/public/bem/100.pdf",
    )
    defined_for = StateCode.MI

    def formula(spm_unit, period, parameters):
        # Overall eligibility requires:
        # 1. Income eligibility
        # 2. Resource eligibility
        # Note: Simplified implementation does not model:
        # - Time limits (not cross-sectionally modelable)
        # - Work requirements (behavioral)
        # - Household composition details (using SPM unit as proxy)

        income_eligible = spm_unit("mi_tanf_income_eligible", period)
        resources_eligible = spm_unit("mi_tanf_resources_eligible", period)

        return income_eligible & resources_eligible
