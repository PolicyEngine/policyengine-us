from policyengine_us.model_api import *


class va_agi(Variable):
    value_type = float
    entity = TaxUnit
    label = "Virginia adjusted federal adjusted gross income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://law.lis.virginia.gov/vacodefull/title58.1/chapter3/article2/"
    )
