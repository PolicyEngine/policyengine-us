from policyengine_us.model_api import *


class de_agi(Variable):
    value_type = float
    entity = TaxUnit
    label = "Delaware adjusted gross income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.DE

    adds = ["de_pre_exclusions_agi"]
    subtracts = ["de_elderly_or_disabled_income_exclusion"]
