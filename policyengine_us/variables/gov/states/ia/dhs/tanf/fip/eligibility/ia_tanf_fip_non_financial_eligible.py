from policyengine_us.model_api import *


class ia_tanf_fip_non_financial_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Iowa FIP non-financial eligible"
    definition_period = MONTH
    reference = "Iowa Code Chapter 239B.2"
    documentation = (
        "Meets Iowa FIP non-financial eligibility requirements including "
        "residency, citizenship, and family composition."
    )
    defined_for = StateCode.IA

    def formula(spm_unit, period, parameters):
        has_eligible_child = spm_unit("ia_tanf_fip_has_eligible_child", period)

        # Check state residency
        state_code = spm_unit.value_from_first_person(
            spm_unit.members("state_code", period)
        )
        is_iowa_resident = state_code == StateCode.IA

        # Citizenship - assume U.S. citizenship or qualified alien status
        # In practice, this would need more detailed implementation
        person = spm_unit.members
        is_citizen = person("is_us_citizen", period)
        has_citizen = spm_unit.any(is_citizen)

        return (
            has_eligible_child  
            & is_iowa_resident  
            & has_citizen 
        )
