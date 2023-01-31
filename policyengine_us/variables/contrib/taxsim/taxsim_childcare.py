from policyengine_us.model_api import *


class taxsim_childcare(Variable):
    value_type = float
    entity = TaxUnit
    label = "Childcare"
    unit = USD
    definition_period = YEAR

    adds = ["tax_unit_childcare_expenses"]
