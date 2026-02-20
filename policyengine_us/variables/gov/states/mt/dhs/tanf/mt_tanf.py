from policyengine_us.model_api import *


class mt_tanf(Variable):
    value_type = float
    entity = SPMUnit
    label = "Montana Temporary Assistance for Needy Families (TANF)"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/montana/Mont-Admin-r-37.78.420",
        "https://dphhs.mt.gov/assets/hcsd/tanfmanual/TANF001.pdf#page=1",
    )
    defined_for = "mt_tanf_eligible"

    def formula(spm_unit, period, parameters):
        standard_payment = spm_unit("mt_tanf_payment_standard", period)
        countable_income = spm_unit("mt_tanf_countable_income", period)
        benefit = max_(standard_payment - countable_income, 0)
        return min_(benefit, standard_payment)
