from policyengine_us.model_api import *


class wv_income_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "West Virginia income tax"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.WV
