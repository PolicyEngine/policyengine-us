from policyengine_us.model_api import *


class ms_agi(Variable):
    value_type = float
    entity = TaxUnit
    label = "Mississippi adjusted gross income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.dor.ms.gov/sites/default/files/Forms/Individual/80100221.pdf#page=14",
        "https://www.dor.ms.gov/sites/default/files/Forms/Individual/80105228.pdf",  # Line 66
    )
    defined_for = StateCode.MS

    # AGI = Income - Total adjustments from gross income
    adds = "gov.states.ms.tax.income.income_sources"
    subtracts = ["ms_agi_adjustments"]
