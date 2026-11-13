from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class la_liheap_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Louisiana LIHEAP income eligible"
    defined_for = StateCode.LA
    reference = (
        "https://www.lhc.la.gov/hubfs/Document%20Libraries/Energy%20Assistance/Louisiana%20LIHEAP%20Service%20Delivery%20Guide%20-%20REVISED%20January%201_%202024.pdf#page=29",
        "https://www.lhc.la.gov/hubfs/Document%20Libraries/Energy%20Assistance/Louisiana%20LIHEAP%20Service%20Delivery%20Guide%20-%20FINAL%20-%20Effective%20April%201%2c%202026.pdf#page=34",
        # PDF pages 9, 11
        "https://liheapch.acf.gov/docs/2026/state-plans/LA_Plan_2026.pdf#page=9",
        "https://www.law.cornell.edu/uscode/text/42/8624#b_2_B",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.la.lhc.liheap.eligibility
        p_hhs = parameters(period).gov.hhs.liheap
        size = spm_unit("la_liheap_household_size", period)
        income = spm_unit("la_liheap_countable_income", period)
        limit = spm_unit("la_liheap_income_limit", period)
        # 42 U.S.C. 8624(b)(2)(B) bars excluding a household on income below 110%
        # of the poverty guideline. The 60% SMI limit falls below that floor from
        # household size 14 in FY2026 (91,855 against 95,865).
        state_group = spm_unit.household("state_group_str", period)
        guideline = fpg(size, state_group, period, parameters, year_lag=p.fpg_year_lag)
        floor = np.round(guideline * p_hhs.fpg_floor, 2)
        return (income <= limit) | (income < floor)
