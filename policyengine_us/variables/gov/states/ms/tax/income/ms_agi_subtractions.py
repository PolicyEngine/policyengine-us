from policyengine_us.model_api import *


class ms_agi_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Mississippi adjustments to federal adjusted gross income"
    unit = USD
    definition_period = YEAR
    reference = "https://www.dor.ms.gov/sites/default/files/Forms/Individual/80100221.pdf#page=13"
    defined_for = StateCode.MS

    adds = "gov.states.ms.tax.income.subtractions.subtractions"
