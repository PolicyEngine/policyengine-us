from policyengine_us.model_api import *


class id_liheap_categorically_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Idaho LIHEAP categorical eligibility"
    definition_period = MONTH
    defined_for = StateCode.ID
    documentation = "Whether household is categorically eligible through SNAP, TANF, or SSI (alias for id_liheap_categorical_eligible)"
    reference = [
        "https://healthandwelfare.idaho.gov/services-programs/idaho-careline/energy-assistance",
    ]

    def formula(spm_unit, period, parameters):
        # Alias for id_liheap_categorical_eligible to handle both naming conventions
        return spm_unit("id_liheap_categorical_eligible", period)
