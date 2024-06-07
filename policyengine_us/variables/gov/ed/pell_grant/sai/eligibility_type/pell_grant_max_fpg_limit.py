from policyengine_us.model_api import *


class pell_grant_max_fpg_limit(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "The maximum income to qualify for the maximum Pell Grant"

    def formula(tax_unit, period, parameters):
        return 0
