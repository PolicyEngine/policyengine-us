from policyengine_us.model_api import *


class co_ccap_num_child_age_eligible(Variable):
    value_type = float
    entity = TaxUnit 
    label = "Colorado child care assistance program eligible"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CO

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        child_age_eligible = person("co_ccap_child_age_eligible", period)
        return tax_unit.sum(child_age_eligible)