from policyengine_us.model_api import *


class va_additions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Virginia additions to federal adjusted gross income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://law.lis.virginia.gov/vacodefull/title58.1/chapter3/article2/",
        "https://www.tax.virginia.gov/sites/default/files/vatax-pdf/2022-760-instructions.pdf#page=24",
    )
    defined_for = StateCode.VA
