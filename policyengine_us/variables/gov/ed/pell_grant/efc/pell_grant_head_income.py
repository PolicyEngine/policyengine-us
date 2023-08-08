from policyengine_us.model_api import *


class pell_grant_head_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Head Income"
    definition_period = YEAR
