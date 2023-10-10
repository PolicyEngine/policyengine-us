from policyengine_us.model_api import *


class va_qualification_total(Variable):
    value_type = float
    entity = TaxUnit
    label = "Virginia aged/blind exemption"
    defined_for = StateCode.VA
    unit = USD
    definition_period = YEAR
    reference = "https://www.tax.virginia.gov/sites/default/files/vatax-pdf/2022-760-instructions.pdf#page=19"

    def formula(tax_unit, period, parameters):
        return (va_qualification_head + va_qualification_spouse) > 0
