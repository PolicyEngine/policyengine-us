from policyengine_us.model_api import *


class ny_college_tuition_credit_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "New York college tuition credit eligible"
    definition_period = YEAR
    reference = "https://www.nysenate.gov/legislation/laws/TAX/606"  # (t)
    defined_for = StateCode.NY

    def formula(tax_unit, period, parameters):
        return ~tax_unit("ny_itemizes", period)
