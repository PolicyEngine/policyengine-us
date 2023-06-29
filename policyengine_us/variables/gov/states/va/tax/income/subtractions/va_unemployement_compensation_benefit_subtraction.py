from policyengine_us.model_api import *


class va_unemployment_compensation_benefit_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Virginia Unemployment Compensation Benefits"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://law.lis.virginia.gov/vacodefull/title58.1/chapter3/article2/"
    )
    defined_for = StateCode.VA
