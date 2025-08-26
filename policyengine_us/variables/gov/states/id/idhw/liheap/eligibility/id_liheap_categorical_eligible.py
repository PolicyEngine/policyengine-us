from policyengine_us.model_api import *


class id_liheap_categorical_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Idaho LIHEAP categorical eligibility"
    definition_period = MONTH
    defined_for = StateCode.ID
    documentation = "Whether household is categorically eligible for Idaho LIHEAP through participation in other programs"
    reference = [
        "https://healthandwelfare.idaho.gov/services-programs/idaho-careline/energy-assistance",
        "45 CFR 96.85(b)",
    ]

    def formula(spm_unit, period, parameters):
        # Households are automatically qualified if they participate in:
        # - SNAP (Food Stamps)
        # - TANF (Temporary Assistance for Needy Families)
        # - SSI (Supplemental Security Income)

        snap = spm_unit("snap", period) > 0
        tanf = spm_unit("tanf", period) > 0
        ssi = spm_unit("ssi", period) > 0

        return snap | tanf | ssi
