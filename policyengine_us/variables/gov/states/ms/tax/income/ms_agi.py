from policyengine_us.model_api import *


class ms_agi(Variable):
    value_type = float
    entity = TaxUnit
    label = "Mississippi adjusted gross income"
    unit = USD
    definition_period = YEAR
    reference = "https://www.dor.ms.gov/sites/default/files/Forms/Individual/80100221.pdf#page=14"
    defined_for = StateCode.MS

    # AGI = Income - Total adjustments from gross income
    adds = ["adjusted_gross_income"]
    subtracts = ["ms_agi_subtractions"]
