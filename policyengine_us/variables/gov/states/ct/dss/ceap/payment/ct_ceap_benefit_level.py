from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class ct_ceap_benefit_level(Variable):
    value_type = int
    entity = SPMUnit
    label = "Connecticut CEAP benefit level"
    definition_period = YEAR
    defined_for = StateCode.CT
    reference = (
        # PDF pages 7,10-11
        "https://portal.ct.gov/dss/-/media/departments-and-agencies/dss/winter-heating-assistance/09012026/ffy-27-liheap-allocation-plan.pdf#page=7",
        "https://www.law.cornell.edu/uscode/text/42/8624#b_5",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ct.dss.ceap.payment
        size = spm_unit("ct_ceap_household_size", period)
        group = spm_unit.household("state_group_str", period)
        guideline = fpg(size, group, period, parameters, year_lag=p.fpg_year_lag)
        income = spm_unit("ct_ceap_countable_income", period)
        level = p.income_level.calc(income / guideline, right=True)
        # Categorical households that fail the income test receive the last
        # level (201% FPG to 60% SMI) even when large-family FPG thresholds
        # would put them in a higher tier. Households the income test admits,
        # including through the federal floor, keep their level whether or not
        # they are categorical: 42 U.S.C. 8624(b)(5) bars differentiating them.
        lowest_level = p.income_level.amounts[-1]
        categorical = spm_unit("ct_ceap_categorically_eligible", period)
        income_eligible = spm_unit("ct_ceap_income_eligible", period)
        return where(categorical & ~income_eligible, lowest_level, level)
