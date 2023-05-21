from policyengine_us.model_api import *


class va_afagi(Variable):
    value_type = float
    entity = TaxUnit
    label = "Adjusted federal adjusted gross income (AFAGI)"
    unit = USD
    definition_period = YEAR
    reference = "https://www.tax.virginia.gov/laws-rules-decisions/rulings-tax-commissioner/13-5"
