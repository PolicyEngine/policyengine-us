from policyengine_us.model_api import *


class az_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona subtractions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.AZ

    adds = "gov.states.az.tax.income.subtractions.subtractions"
