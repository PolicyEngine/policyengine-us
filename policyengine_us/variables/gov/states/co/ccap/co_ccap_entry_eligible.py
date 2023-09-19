from policyengine_us.model_api import *


class co_ccap_entry_eligible(Variable):
    value_type = bool
    entity = TaxUnit 
    label = "Colorado child care assistance program eligible"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CO

    def formula(tax_unit, period, parameters):
        income_eligible = tax_unit("co_ccap_income_eligible", period)
        child_age_eligible = tax_unit("co_ccap_num_child_age_eligible", period) > 0
        return tax_unit.sum(income_eligible & child_age_eligible)