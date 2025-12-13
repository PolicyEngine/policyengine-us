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
        person = spm_unit.members

        # Must meet demographic requirements (age, deprivation)
        # Use federal demographic eligibility
        demographic_eligible = spm_unit("is_demographic_tanf_eligible", period)

        # Must have at least one citizen or legal immigrant
        # Per MI FIP requirements: "You must have at least one citizen or
        # qualified lawful immigrant in your family"
        has_citizen = spm_unit.any(
            person("is_citizen_or_legal_immigrant", period)
        )

        # Must meet income eligibility
        income_eligible = spm_unit("mi_fip_income_eligible", period)

        # Must meet resource eligibility
        resources_eligible = spm_unit("mi_fip_resources_eligible", period)

        # Note: Simplified implementation does not model:
        # - Time limits (60 months as of April 2025)
        # - Work requirements (behavioral)

        return (
            demographic_eligible
            & has_citizen
            & income_eligible
            & resources_eligible
        )
