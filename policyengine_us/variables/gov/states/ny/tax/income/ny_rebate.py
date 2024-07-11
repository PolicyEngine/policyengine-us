from policyengine_us.model_api import *


class ny_rebate(Variable):
    value_type = float
    entity = TaxUnit
    label = "NY rebate"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NY

    adds = "gov.states.ny.tax.income.rebate"
