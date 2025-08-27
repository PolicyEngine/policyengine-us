from policyengine_us.model_api import *


class id_liheap_crisis_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Idaho LIHEAP crisis assistance eligibility"
    definition_period = MONTH
    defined_for = StateCode.ID
    documentation = "Household is in a crisis situation eligible for emergency LIHEAP assistance"
    reference = [
        "https://healthandwelfare.idaho.gov/services-programs/idaho-careline/energy-assistance",
    ]

    def formula(spm_unit, period, parameters):
        # Crisis eligibility requires being LIHEAP eligible AND having a crisis situation
        # For simulation purposes, this is an input variable that would be determined
        # based on utility disconnection notices, past due bills, or fuel shortage
        return False  # Default to False, should be input as test data
