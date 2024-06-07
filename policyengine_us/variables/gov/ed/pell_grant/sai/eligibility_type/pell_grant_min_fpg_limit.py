from policyengine_us.model_api import *


class pell_grant_min_fpg_percent_limit(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "The maximum FPG percent to qualify for the minimum Pell Grant"

    def formula(tax_unit, period, parameters):
        return 0
