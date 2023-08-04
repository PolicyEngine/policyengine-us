from policyengine_us.model_api import *


class mt_agi(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montana Adjusted Gross Income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MT

    # def formula(tax_unit, period, parameters):
    #    us_agi = tax_unit("adjusted_gross_income", period)
    #    mt_adds = tax_unit("mt_total_additions", period)
    #    mt_subs = tax_unit("mt_total_subtractions", period)
    #    return max_(0, us_agi + mt_adds - mt_subs)
