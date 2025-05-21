from policyengine_us.model_api import *


class ct_income_tax_recapture(Variable):
    value_type = float
    entity = TaxUnit
    label = "Connecticut income tax recapture"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CT

    adds = [
        "ct_income_tax_low_tax_recapture",
        "ct_income_tax_middle_tax_recapture",
        "ct_income_tax_high_tax_recapture",
    ]
