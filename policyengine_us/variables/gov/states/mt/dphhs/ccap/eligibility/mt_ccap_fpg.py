from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class mt_ccap_fpg(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    definition_period = MONTH
    label = "Montana CCAP monthly federal poverty guideline"
    defined_for = StateCode.MT
    reference = "https://dphhs.mt.gov/assets/ecfsd/childcare/policymanual/SlidingFeeScale07012023.pdf#page=1"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.mt.dphhs.ccap.income
        size = spm_unit("spm_unit_size", period.this_year)
        state_group = spm_unit.household("state_group_str", period.this_year)
        annual_fpg = fpg(size, state_group, period, parameters, year_lag=p.fpg_year_lag)
        return annual_fpg / MONTHS_IN_YEAR
