from policyengine_us.model_api import *


class va_agi(Variable):
    value_type = float
    entity = Person
    label = "Virginia Adjusted Gross Income (VAGI)"
    unit = USD
    definition_period = YEAR
    reference = "https://www.tax.virginia.gov/laws-rules-decisions/rulings-tax-commissioner/13-5"
    defined_for = StateCode.VA
