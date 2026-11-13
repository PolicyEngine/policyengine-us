from policyengine_us.model_api import *


class child_care_charges_providers_absorb(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "Child care charges providers absorb under subsidy rules"
    documentation = (
        "Charges above a child care subsidy program's rate that the program's "
        "rules bar the provider from collecting from the family."
    )
    unit = USD

    adds = ["co_ccap_charges_above_rate"]
