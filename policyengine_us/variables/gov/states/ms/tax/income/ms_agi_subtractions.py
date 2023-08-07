from policyengine_us.model_api import *


class ms_agi_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "MS AGI subtractions from federal AGI"
    unit = USD
    definition_period = YEAR
    reference = "https://www.dor.ms.gov/sites/default/files/Forms/Individual/80100221.pdf#page=13"
    defined_for = StateCode.MS

    def formula(tax_unit, period, parameters):
        agi = tax_unit("adjusted_gross_income", period)

        return agi
