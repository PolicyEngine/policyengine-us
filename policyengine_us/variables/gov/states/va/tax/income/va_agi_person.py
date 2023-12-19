from policyengine_us.model_api import *


class va_agi_person(Variable):
    value_type = float
    entity = Person
    label = "Virginia Adjusted Gross Income (VAGI) for each individual"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://law.lis.virginia.gov/vacodefull/title58.1/chapter3/article2/"
    )
    defined_for = StateCode.VA
