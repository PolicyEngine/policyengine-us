from policyengine_us.model_api import *


class id_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Idaho subtractions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.ID
    adds = "gov.states.id.tax.income.subtractions.subtractions"
