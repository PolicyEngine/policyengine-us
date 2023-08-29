from policyengine_us.model_api import *


class co_additions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Colorado additions to federal taxable income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CO
