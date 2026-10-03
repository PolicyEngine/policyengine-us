from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class ct_ceap_benefit_level(Variable):
    value_type = int
    entity = SPMUnit
    label = "Connecticut CEAP benefit level"
    definition_period = YEAR
    defined_for = StateCode.CT
    reference = "https://portal.ct.gov/dss/-/media/departments-and-agencies/dss/winter-heating-assistance/09012026/ffy-27-liheap-allocation-plan.pdf#page=7,10,11"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ct.dss.ceap.payment
        size = spm_unit("ct_ceap_household_size", period)
        group = spm_unit.household("state_group_str", period)
        guideline = fpg(
            max_(size, 1), group, period, parameters, year_lag=p.fpg_year_lag
        )
        income = spm_unit("ct_ceap_countable_income", period)
        level = p.income_level.calc(income / guideline, right=True)
        # Categorical households above the SMI ceiling receive Level 3 even
        # when large-family FPG thresholds would put them in a higher tier.
        limit = spm_unit("ct_ceap_income_limit", period)
        return where(income > limit, 3, level)
