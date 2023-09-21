from policyengine_us.model_api import *


class co_ccap_re_determination_eligible(Variable):
    value_type = bool
    entity = TaxUnit 
    label = "Colorado child care assistance program eligible"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CO

    def formula(tax_unit, period, parameters):

        return tax_unit("co_ccap_hhs_smi_eligible", period)