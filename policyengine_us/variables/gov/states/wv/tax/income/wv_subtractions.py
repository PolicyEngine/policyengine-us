from policyengine_us.model_api import *


class wv_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "West Virginia subtractions from the adjusted gross income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.WV
    adds = "gov.states.wv.tax.income.subtractions.subtractions"
