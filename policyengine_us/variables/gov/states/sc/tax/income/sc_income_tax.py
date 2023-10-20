from policyengine_us.model_api import *


class sc_income_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "South Carolina income tax"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.SC
