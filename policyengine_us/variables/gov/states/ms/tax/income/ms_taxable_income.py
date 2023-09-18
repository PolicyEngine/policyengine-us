from policyengine_us.model_api import *


class ms_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Mississippi taxable income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.dor.ms.gov/sites/default/files/Forms/Individual/80100221.pdf#page=13",
        "https://www.dor.ms.gov/sites/default/files/Forms/Individual/80105228.pdf",  # Line 38 - 49,
    )
    defined_for = StateCode.MS

    adds = "gov.states.ms.tax.income.income_sources"
