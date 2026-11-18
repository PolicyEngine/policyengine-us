from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class nj_liheap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "New Jersey LIHEAP regular heating eligibility"
    defined_for = StateCode.NJ
    reference = (
        # PDF pages 5, 6, 7, 11, 12.
        "https://www.nj.gov/dca/dhcr/offices/docs/FY2026%20LIHEAP%20Handbook%20.pdf#page=5",
        # PDF pages 5, 6, 7, 12, 13.
        "https://www.nj.gov/dca/dhcr/offices/docs/FY2027%20LIHEAP%20Handbook.pdf#page=5",
        "https://www.law.cornell.edu/regulations/new-jersey/N-J-A-C-5-49-2-2",
        "https://www.law.cornell.edu/regulations/new-jersey/N-J-A-C-5-49-2-3",
        "https://www.nj.gov/bpu/newsroom/2021/approved/20211019.html",
        "https://www.law.cornell.edu/uscode/text/42/8624",
    )
    documentation = (
        "Automatic enrollment does not waive the income test, and regular heating has "
        "no asset test. The program is modeled from FY2022, when the 60% SMI standard "
        "began; earlier periods return false. Striker and institutional-residence exclusions, full "
        "utility-allowance coverage and payments by people outside the household need "
        "inputs not available here. Unknown county is unsupported, not a legal denial."
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.nj.dca.liheap.eligibility
        heat_in_rent = spm_unit("heat_expense_included_in_rent", period)
        # Handbook 2.2 (page 6) and N.J.A.C. 5:49-2.3(b)1-2 deny public housing
        # and rent-subsidy households only when the subsidy covers the heat.
        subsidized = spm_unit(
            "receives_housing_assistance", period
        ) | spm_unit.household("is_in_public_housing", period)
        person = spm_unit.members
        dependent_students_only = spm_unit.all(
            person("is_full_time_student", period)
            & person("is_tax_unit_dependent", period)
        )
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
        income_eligible = (income <= limit) | (income < floor)
        # The modeled 60% SMI rules begin with FY2022 (BPU, October 19, 2021);
        # the earlier poverty-level standard is not encoded.
        return (
            p.in_effect
            & (spm_unit("has_heating_expense", period) | heat_in_rent)
            & ~(heat_in_rent & subsidized)
            & ~dependent_students_only
            & (size > 0)
            & income_eligible
        )
