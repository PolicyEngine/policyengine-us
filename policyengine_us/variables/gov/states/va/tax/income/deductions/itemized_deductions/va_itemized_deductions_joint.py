from policyengine_us.model_api import *


class va_itemized_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Virginia itemized deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://law.lis.virginia.gov/vacodefull/title58.1/chapter3/article2/","§ 58.1-322.03.(1.a.)",
        "https://www.tax.virginia.gov/sites/default/files/vatax-pdf/2022-760-instructions.pdf#page=18"
    )
    defined_for = StateCode.VA

    adds = ["tax_liability_if_itemizing"]
