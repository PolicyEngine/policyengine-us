from policyengine_us.model_api import *


class sc_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "South Carolina subtractions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.SC
    adds = "gov.states.sc.tax.income.subtractions.subtractions"
