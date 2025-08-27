from policyengine_us.model_api import *


class id_liheap_crisis_benefit(Variable):
    value_type = float
    entity = SPMUnit
    label = "Idaho LIHEAP crisis heating assistance benefit"
    definition_period = MONTH
    defined_for = StateCode.ID
    unit = USD
    documentation = "Crisis heating assistance benefit amount for Idaho LIHEAP (year-round availability)"
    reference = [
        "https://healthandwelfare.idaho.gov/services-programs/idaho-careline/energy-assistance",
        "45 CFR 96.83",
    ]

    def formula(spm_unit, period, parameters):
        # Crisis assistance is available year-round
        # Must be eligible for LIHEAP
        eligible = spm_unit("id_liheap_eligible", period)

        # Get crisis benefit parameters
        p = parameters(period).gov.states.id.idhw.liheap.crisis_benefit
        maximum_benefit = p.maximum

        # Crisis assistance is for emergency situations:
        # - At risk of utility disconnection
        # - Have a past due utility balance
        # - Have less than 48 hours of bulk fuel
        # - Cannot have received crisis assistance in last 12 months

        # For this implementation, we assume eligible households may receive
        # crisis assistance when needed (simplified model)
        # In practice, this would require additional variables to track:
        # - Past due balances
        # - Previous crisis assistance receipt
        # - Emergency heating situations

        # Return 0 for now, as crisis benefits are situation-specific
        # This could be expanded with additional emergency condition variables
        return where(eligible, 0, 0)
