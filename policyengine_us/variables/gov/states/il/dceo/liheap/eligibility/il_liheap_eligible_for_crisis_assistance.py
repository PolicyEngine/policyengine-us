from policyengine_us.model_api import *


class il_liheap_eligible_for_crisis_assistance(Variable):
    value_type = bool
    entity = SPMUnit
    label = "SPM Unit has utility disconnect notice under Illinois LIHEAP crisis assistance program"
    definition_period = YEAR
    defined_for = StateCode.IL
    reference = "https://dceo.illinois.gov/communityservices/utilitybillassistance.html"

    # Crisis assistance is available when utility is about to be disconnected
    # For modeling purposes, this defaults to False as we don't have disconnect status
    # In a real implementation, this would check for utility disconnect notices
