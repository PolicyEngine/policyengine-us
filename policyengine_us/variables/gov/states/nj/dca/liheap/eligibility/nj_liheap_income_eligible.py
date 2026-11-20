from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class nj_liheap_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "New Jersey LIHEAP income eligibility"
    defined_for = StateCode.NJ
    reference = (
        # PDF page 7.
        "https://www.nj.gov/dca/dhcr/offices/docs/FY2026%20LIHEAP%20Handbook%20.pdf#page=7",
        # PDF page 7.
        "https://www.nj.gov/dca/dhcr/offices/docs/FY2027%20LIHEAP%20Handbook.pdf#page=7",
        "https://www.law.cornell.edu/uscode/text/42/8624",
    )
    documentation = (
        "The monthly income test that regular heating (handbook 2.3.A) and "
        "medically necessary cooling (handbook 3.4.A, income-eligible households) "
        "share: income at or below 60% of state median income, or below the "
        "federal 110% poverty floor."
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.nj.dca.liheap.eligibility
        size = spm_unit("nj_liheap_household_size", period)
        income = spm_unit("nj_liheap_countable_income", period)
        limit = spm_unit("nj_liheap_income_limit", period)
        # 42 U.S.C. 8624(b)(2)(B) bars excluding a household on income below 110%
        # of the poverty guideline. The 60% SMI limit falls below that floor from
        # household size 28 to 32 in FY2022 to FY2027.
        p_hhs = parameters(period).gov.hhs.liheap
        state_group = spm_unit.household("state_group_str", period)
        guideline = fpg(size, state_group, period, parameters, year_lag=p.fpg_year_lag)
        floor = np.round(guideline * p_hhs.fpg_floor, 2)
        return (income <= limit) | (income < floor)
