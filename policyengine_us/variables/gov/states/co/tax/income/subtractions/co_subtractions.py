from policyengine_us.model_api import *


class co_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Colorado subtractions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CO

    adds = "gov.states.co.tax.income.subtractions.subtractions"
