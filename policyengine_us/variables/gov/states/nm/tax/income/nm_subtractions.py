from policyengine_us.model_api import *


class nm_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Mexico income subtractions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NM

    adds = "gov.states.nm.tax.income.subtractions"
