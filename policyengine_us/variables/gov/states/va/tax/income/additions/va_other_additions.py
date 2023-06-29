from policyengine_us.model_api import *


class va_other_additions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Virginia other additions to Federal Adjusted Gross Income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://law.lis.virginia.gov/vacodefull/title58.1/chapter3/article2/"
    )
    defined_for = StateCode.VA
