from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg
from policyengine_us.variables.gov.states.ga.dfcs.liheap.eligibility._ga_liheap_housing import (
    ga_liheap_has_direct_payment_route,
    ga_liheap_has_electric_vendor_route,
)


class ga_liheap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Georgia LIHEAP ordinary eligibility"
    defined_for = StateCode.GA
    reference = (
        # PDF pages 5, 8-9, 30, 43
        "https://liheapch.acf.gov/docs/2026/state-plans/GA_Plan_2026.pdf#page=5",
        "https://liheapch.acf.gov/docs/2025/state-plans/GA_Plan_2025.pdf#page=43",
        # PDF pages 3-4, 50, 56-57, 75, 82, 89
        "https://liheapch.acf.gov/sites/default/files/webfiles/docs/2023/manuals/GA_PolicyManual_2023.pdf#page=3",
        # PAMMS chapter 100, export dated 2026-10-16.
        "https://pamms.dhs.ga.gov/dfcs/_exports/liheap.pdf#page=4",
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
        income_eligible = (income <= limit) | (income < floor)
        heating_type = spm_unit("heating_type", period)
        heating_expense = spm_unit("heating_expense", period)
        # Explicit heating responsibility can qualify with no current bill.
        # A positive primary bill also establishes burden with heat in rent,
        # including subsidized housing (PAMMS chapter 100: "a vendor
        # bill/statement for the main heating source"). Heat-in-rent renters
        # also qualify when billed directly for electric, subsidized or not
        # (manual pages 4, 57 and 89), or when unsubsidized with all utilities
        # in rent (page 89). The rent flag alone is insufficient.
        # FY2026 plan item 2.3 (page 8) answers No to additional or differing
        # eligibility policies for subsidized renters and renters with utilities in
        # rent, while the manual applies energy-burden rules to both (pages 4, 57,
        # 82 and 89); this follows the manual.
        energy_burden = (
            spm_unit("has_heating_expense", period)
            | (heating_expense > 0)
            | ga_liheap_has_direct_payment_route(spm_unit, period)
            | ga_liheap_has_electric_vendor_route(spm_unit, period)
        )
        # Pure-assistance categorical eligibility requires actual receipt by
        # every member and assistance-only income/resources. Aggregate TANF/SNAP
        # inputs cannot establish those facts, so this uses the ordinary test.
        # Account credits of $1,000+ and administrative household exclusions
        # also need unavailable inputs; the selected heating account is assumed
        # to satisfy those rules. Annual expense is not an account-credit proxy.
        # A household of lawful immigrants only has size > 0 and qualifies;
        # see the manual note in ga_liheap_household_size.
        return (
            (size > 0)
            & income_eligible
            & energy_burden
            & (heating_type != heating_type.possible_values.NONE)
        )
