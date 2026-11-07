from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class or_liheap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Oregon LIHEAP regular heating eligibility"
    defined_for = StateCode.OR
    # Manual PDF pages 11, 30, 36, 61, 77, 93-94; OAR 813-200-0020(1)(b).
    reference = (
        "https://www.oregon.gov/ohcs/energy-weatherization/Documents/2026%20Final%20Energy%20Assistance%20Intake%20Operations%20%26%20Policy%20Manual.pdf#page=61",
        "https://www.law.cornell.edu/regulations/oregon/Or-Admin-Code-SS-813-200-0020",
        "https://www.law.cornell.edu/uscode/text/42/8624",
    )
    documentation = (
        "SPM members approximate the economic household, with identity and SSN "
        "verification assumed complete. The energy burden test follows OAR "
        "813-200-0020(1)(b) and the manual's energy burden table: subsidized housing "
        "with heat included in rent is excluded even when the household pays a "
        "separate non-heating utility bill. The Oregon sources do not prescribe a "
        "SNAP immigration test. No asset or categorical income test applies. "
        "Institutional residence, tribal duplicate awards, documentation and "
        "application timing are not modeled. A zero benefit above size 12 or for an "
        "unknown county denotes unsupported schedule coverage, not a legal denial."
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states["or"].ohcs.liheap.eligibility
        p_hhs = parameters(period).gov.hhs.liheap
        heat_in_rent = spm_unit("heat_expense_included_in_rent", period)
        subsidized = spm_unit(
            "receives_housing_assistance", period
        ) | spm_unit.household("is_in_public_housing", period)
        heating_cost = spm_unit("has_heating_expense", period) | heat_in_rent
        income = spm_unit("or_liheap_countable_income", period)
        limit = spm_unit("or_liheap_income_limit", period)
        # 42 U.S.C. 8624(b)(2)(B) bars excluding a household on income below 110%
        # of the poverty guideline. The 60% SMI limit falls below that floor from
        # household size 19 in PY2025 and size 20 in PY2026 and PY2027.
        size = spm_unit("spm_unit_size", period)
        state_group = spm_unit.household("state_group_str", period)
        guideline = fpg(size, state_group, period, parameters, year_lag=p.fpg_year_lag)
        floor = np.round(guideline * p_hhs.fpg_floor, 2)
        income_eligible = (income <= limit) | (income < floor)
        return heating_cost & ~(heat_in_rent & subsidized) & income_eligible
