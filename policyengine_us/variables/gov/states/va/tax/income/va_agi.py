from policyengine_us.model_api import *


class va_agi(Variable):
    value_type = float
    entity = TaxUnit
    label = "Adjusted federal adjusted gross income (VAGI)"
    unit = USD
    definition_period = YEAR
    reference = "https://law.lis.virginia.gov/vacodefull/title58.1/chapter3/article2/"
