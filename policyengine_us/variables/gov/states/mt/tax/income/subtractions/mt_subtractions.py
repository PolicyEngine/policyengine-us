from policyengine_us.model_api import *


class mt_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montana subtractions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MT

    adds = "gov.states.mt.tax.income.subtractions.subtractions"
