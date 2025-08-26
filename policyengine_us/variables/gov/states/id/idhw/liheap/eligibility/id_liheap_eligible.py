from policyengine_us.model_api import *


class id_liheap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Idaho LIHEAP eligibility"
    definition_period = MONTH
    defined_for = StateCode.ID
    documentation = "Whether household is eligible for Idaho LIHEAP assistance"
    reference = [
        "https://healthandwelfare.idaho.gov/services-programs/idaho-careline/energy-assistance",
        "45 CFR 96.85",
    ]

    def formula(spm_unit, period, parameters):
        # Household is eligible if they meet income requirements OR are categorically eligible
        income_eligible = spm_unit("id_liheap_income_eligible", period)
        categorical_eligible = spm_unit(
            "id_liheap_categorical_eligible", period
        )

        return income_eligible | categorical_eligible
