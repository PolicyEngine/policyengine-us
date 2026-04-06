from policyengine_us.model_api import *


class mi_fip_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Michigan Family Independence Program"
    definition_period = MONTH
    reference = (
        "https://www.michigan.gov/mdhhs/-/media/Project/Websites/mdhhs/Inside-MDHHS/Reports-and-Statistics---Human-Services/State-Plans-and-Federal-Regulations/TANF_State_Plan_2023.pdf",
        "https://mdhhs-pres-prod.michigan.gov/olmweb/ex/bp/public/bem/100.pdf",
    )
    defined_for = StateCode.MI

    def formula(spm_unit, period, parameters):
        demographic_eligible = spm_unit("is_demographic_tanf_eligible", period)
        immigration_eligible = (
            add(spm_unit, period, ["is_citizen_or_legal_immigrant"]) > 0
        )
        income_eligible = spm_unit("mi_fip_income_eligible", period)
        resources_eligible = spm_unit("mi_fip_resources_eligible", period)

        # NOTE: Time limits and work requirements not modeled

        return (
            demographic_eligible
            & immigration_eligible
            & income_eligible
            & resources_eligible
        )
