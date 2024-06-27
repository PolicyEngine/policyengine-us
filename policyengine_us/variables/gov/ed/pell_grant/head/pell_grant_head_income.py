from policyengine_us.model_api import *


class pell_grant_primary_income(Variable):
    value_type = float
    entity = TaxUnit
    unit = USD
    label = "Pell Grant head income"
    definition_period = YEAR
