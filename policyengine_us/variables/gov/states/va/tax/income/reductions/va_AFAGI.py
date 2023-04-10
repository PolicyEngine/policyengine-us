from policyengine_us.model_api import *


class va_afagi(Variable):
    value_type = float
    entity = TaxUnit
    label = "Available Federal adjusted gross income"
    unit = USD
    definition_period = YEAR
    reference = "https://www.tax.virginia.gov/sites/default/files/vatax-pdf/2022-760-instructions.pdf#page=16"
    defined_for = StateCode.VA
