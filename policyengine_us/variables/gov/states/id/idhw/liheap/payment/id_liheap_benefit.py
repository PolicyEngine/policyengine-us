from policyengine_us.model_api import *


class id_liheap_benefit(Variable):
    value_type = float
    entity = SPMUnit
    label = "Idaho LIHEAP total benefit"
    definition_period = MONTH
    defined_for = StateCode.ID
    unit = USD
    documentation = (
        "Total Idaho LIHEAP benefit combining seasonal and crisis assistance"
    )
    reference = [
        "https://healthandwelfare.idaho.gov/services-programs/idaho-careline/energy-assistance",
        "45 CFR 96.83",
    ]
    adds = ["gov.states.id.idhw.liheap.payment"]

    def formula(spm_unit, period, parameters):
        # Total LIHEAP benefit is the sum of:
        # - Seasonal heating assistance (October-March)
        # - Crisis assistance (year-round, situation-specific)
        # Note: Weatherization is handled separately as a service, not cash benefit

        seasonal_benefit = spm_unit("id_liheap_seasonal_benefit", period)
        crisis_benefit = spm_unit("id_liheap_crisis_benefit", period)

        # Idaho provides one benefit payment per program year for seasonal assistance
        # Crisis assistance limited to once per 12 months
        # Benefits are paid directly to utility providers, not households

        return seasonal_benefit + crisis_benefit
