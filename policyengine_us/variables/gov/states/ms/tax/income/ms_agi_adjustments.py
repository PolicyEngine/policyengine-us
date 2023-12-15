from policyengine_us.model_api import *


class ms_agi_adjustments(Variable):
    value_type = float
    entity = Person
    label = "Mississippi adjustments to federal adjusted gross income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.dor.ms.gov/sites/default/files/Forms/Individual/80100221.pdf#page=13",
        "https://www.dor.ms.gov/sites/default/files/Forms/Individual/80105228.pdf",  # Line 50 - 66
    )
    defined_for = StateCode.MS

    adds = "gov.states.ms.tax.income.adjustments.adjustments"
