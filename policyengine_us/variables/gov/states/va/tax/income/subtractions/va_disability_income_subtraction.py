from policyengine_us.model_api import *


class va_disability_income_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Virginia disability income subtraction"
    defined_for = StateCode.VA
    unit = USD
    definition_period = YEAR
    reference = "https://law.lis.virginia.gov/vacodefull/title58.1/chapter3/article2/"
    adds = ["va_disability_income_subtraction_person"]
