from policyengine_us.model_api import *


class subsidized_housing(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Whether household lives in subsidized housing"
    definition_period = YEAR
    reference = "https://liheapch.acf.hhs.gov/tables/FY2016/subsidize.htm#OR"
