from policyengine_us.model_api import *


class id_liheap_crisis_heating_amount(Variable):
    value_type = float
    entity = SPMUnit
    label = "Idaho LIHEAP crisis heating assistance amount"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.ID
    documentation = "Crisis heating assistance payment amount"
    reference = [
        "https://healthandwelfare.idaho.gov/services-programs/idaho-careline/energy-assistance",
    ]

    def formula(spm_unit, period, parameters):
        # Crisis payment for households in crisis situations
        eligible = spm_unit("id_liheap_eligible", period)
        crisis = spm_unit("id_liheap_crisis_eligible", period)

        # Get crisis benefit maximum
        p = parameters(period).gov.states.id.idhw.liheap.crisis_benefit

        # For simulation, provide a crisis benefit amount
        # In reality, amount depends on crisis severity and need
        return where(
            eligible & crisis, p.maximum * 0.5, 0
        )  # Use 50% of max for simulation
