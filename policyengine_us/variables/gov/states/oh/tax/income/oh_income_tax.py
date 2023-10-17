from policyengine_us.model_api import *


class oh_income_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Ohio income tax"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.OH
