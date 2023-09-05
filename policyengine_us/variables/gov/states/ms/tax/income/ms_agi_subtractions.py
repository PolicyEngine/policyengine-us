from policyengine_us.model_api import *


class ms_agi_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "MS AGI additions to federal AGI"
    unit = USD
    definition_period = YEAR
    reference = "https://www.dor.ms.gov/sites/default/files/Forms/Individual/80100221.pdf#page=13"
    defined_for = StateCode.MS

    def formula(tax_unit, period, parameters):
        # Line 61: deduct 50% of the federal self-employment taxes imposed.
        self_employment = add(tax_unit, period, ["self_employment_tax"])
        return self_employment * 0.5
