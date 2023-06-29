from policyengine_us.model_api import *


class va_itemized_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Virginia itemized deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://law.lis.virginia.gov/vacodefull/title58.1/chapter3/article2/"
    )
    defined_for = StateCode.VA

    adds = ["tax_unit_itemizes"]
