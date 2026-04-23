from policyengine_us.model_api import *


class taxsim_mn_child_tax_credit_component(Variable):
    value_type = float
    entity = TaxUnit
    label = "Minnesota child tax credit component"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MN

    def formula(tax_unit, period, parameters):
        combined_credit = tax_unit("mn_child_and_working_families_credits", period)
        working_family_credit = tax_unit("mn_wfc", period)
        return max_(0, combined_credit - working_family_credit)
