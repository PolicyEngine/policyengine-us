from policyengine_us.model_api import *


class va_retirement_plan_taxed_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Virginia Retirement Plan Income Previously Taxed by Another State"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://law.lis.virginia.gov/vacodefull/title58.1/chapter3/article2/",
        "§ 58.1-322.02.(11.)",
        "https://www.tax.virginia.gov/sites/default/files/vatax-pdf/2022-760-instructions.pdf#page=26",
    )
    defined_for = StateCode.VA
