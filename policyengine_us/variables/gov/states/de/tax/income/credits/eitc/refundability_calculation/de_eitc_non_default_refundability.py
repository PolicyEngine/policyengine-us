from policyengine_us.model_api import *


class de_eitc_non_default_refundability(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Filer does not claim the refundable Virginia EITC based on income tax liability"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.DE
    default_value = False
