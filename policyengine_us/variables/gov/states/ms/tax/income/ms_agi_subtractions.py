from policyengine_us.model_api import *


class ca_agi_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "MS AGI subtractions from federal AGI"
    unit = USD
    definition_period = YEAR
    reference = "https://www.dor.ms.gov/sites/default/files/Forms/Individual/80100221.pdf"
    defined_for = StateCode.MS

    def formula(tax_unit, period, parameters):
        # tax_unit: (line 50 + ... + 64) - (line 38 + ... + 48)
        return
