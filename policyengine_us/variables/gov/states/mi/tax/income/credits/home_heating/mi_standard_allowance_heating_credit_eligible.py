from policyengine_us.model_api import *


class mi_standard_allowance_heating_credit_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Standard allowance can be claimed"
    definition_period = YEAR
    defined_for = StateCode.MI