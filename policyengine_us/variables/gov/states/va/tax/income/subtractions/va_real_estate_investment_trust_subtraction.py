from policyengine_us.model_api import *


class va_real_estate_investment_trust_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Virginia Real Estate Investment Trust subtraction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://law.lis.virginia.gov/vacodefull/title58.1/chapter3/article2/"
    )
    defined_for = StateCode.VA
