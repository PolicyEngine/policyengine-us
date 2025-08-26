from policyengine_us.model_api import *


class id_liheap_weatherization_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Idaho LIHEAP weatherization program eligibility"
    definition_period = MONTH
    defined_for = StateCode.ID
    documentation = "Whether household meets Idaho LIHEAP weatherization income requirements (200% FPL)"
    reference = [
        "https://healthandwelfare.idaho.gov/services-programs/idaho-careline/energy-assistance",
        "45 CFR 96.83(b)",
    ]

    def formula(spm_unit, period, parameters):
        # Weatherization uses 200% Federal Poverty Level, not 60% SMI
        return spm_unit("id_liheap_weatherization_income_eligible", period)
