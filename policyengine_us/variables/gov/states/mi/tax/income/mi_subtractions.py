from policyengine_us.model_api import *


class mi_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Michigan subtractions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MI

    adds = "gov.states.mi.tax.income.subtractions"
