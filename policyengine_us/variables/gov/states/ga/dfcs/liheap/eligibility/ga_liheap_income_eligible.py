from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class ga_liheap_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Georgia LIHEAP income eligible"
    defined_for = StateCode.GA
    reference = (
        # FY2026 state plan sections 2.1 (heating) and 3.1 (cooling) and
        # assurance 2.
        # PDF pages 8, 10, 43
        "https://liheapch.acf.gov/docs/2026/state-plans/GA_Plan_2026.pdf#page=8",
        "https://liheapch.acf.gov/docs/2025/state-plans/GA_Plan_2025.pdf#page=43",
        "https://www.law.cornell.edu/uscode/text/42/8624#b_2_B",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ga.dfcs.liheap.eligibility
        p_hhs = parameters(period).gov.hhs.liheap
        size = spm_unit("ga_liheap_household_size", period)
        income = spm_unit("ga_liheap_income", period)
        limit = spm_unit("ga_liheap_income_limit", period)
        # 42 U.S.C. 8624(b)(2)(B) bars excluding a household on income below 110%
        # of the poverty guideline. The 60% SMI limit falls below that floor from
        # household size 16 in FY2025 and FY2026. The printed matrices do too: size
        # 16 prints $102,926 in FY2025 (floor $105,336) and $107,634 in FY2026
        # (floor $107,965). Georgia assures the floor (FY2025 and FY2026 plans,
        # page 43), so the floor governs; the limit keeps the printed table.
        state_group = spm_unit.household("state_group_str", period)
        guideline = fpg(size, state_group, period, parameters, year_lag=p.fpg_year_lag)
        floor = np.round(guideline * p_hhs.fpg_floor, 2)
        return (income <= limit) | (income < floor)
