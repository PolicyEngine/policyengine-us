from policyengine_us.model_api import *


class pell_grant_countable_assets(Variable):
    value_type = float
    entity = Person
    label = "Pell Grant countable assets"
    unit = USD
    quantity_type = STOCK
    definition_period = YEAR
