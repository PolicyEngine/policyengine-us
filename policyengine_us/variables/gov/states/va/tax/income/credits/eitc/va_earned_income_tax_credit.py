from policyengine_us.model_api import *


class va_low_income_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Virginia low income tax credit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.VA

    def formula(tax_unit, period, parameters):