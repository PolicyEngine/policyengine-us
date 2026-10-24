from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class mo_liheap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Eligible for Missouri LIHEAP Energy Assistance"
    documentation = "A Missouri household with at least one citizen or legal immigrant member that meets the income limit or the federal 110 percent poverty floor, has resources within the resource limit, pays for heat either through its own fuel bill or through unsubsidized rent that includes heat, and does not heat with coal. Not modeled: the exclusions in 13 CSR 40-19.020(7)(B), (C) and (E)-(H) (nursing or boarding homes, hotels and shelters, Department of Mental Health transitional living, fuel credit balances over $500, self-cut wood and shared-meter dwellings) and the limit of one Energy Assistance payment per household per year."
    reference = (
        # PDF pages 2-3
        "https://www.sos.mo.gov/cmsimages/adrules/csr/current/13csr/13c40-19.pdf#page=2",
        "https://liheapch.acf.gov/docs/2026/state-plans/MO_Plan_2026.pdf#page=8",
        # PDF pages 40, 42-43, 122
        "https://dss.mo.gov/sites/mydss/files/media/pdf/2025/10/liheap-policy-procedure-manual.pdf#page=40",
        "https://www.law.cornell.edu/uscode/text/42/8624#b_2_B",
    )
    defined_for = StateCode.MO

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.mo.dss.liheap.eligibility
        size = spm_unit("mo_liheap_household_size", period)
        income = spm_unit("mo_liheap_countable_income", period)
        limit = spm_unit("mo_liheap_income_limit", period)
        # 42 U.S.C. 8624(b)(2)(B) bars excluding a household on income below 110%
        # of the poverty guideline. The 60% SMI limit falls below that floor from
        # household size 16 in FFY2026 and FFY2027.
        state_group = spm_unit.household("state_group_str", period)
        guideline = fpg(size, state_group, period, parameters, year_lag=p.fpg_year_lag)
        floor = np.round(guideline * parameters(period).gov.hhs.liheap.fpg_floor, 2)
        income_eligible = (income <= limit) | (income < floor)
        resource_eligible = spm_unit("spm_unit_cash_assets", period) <= p.resource_limit
        # 13 CSR 40-19.020(7)(D): subsidized housing is ineligible unless the
        # household pays an energy supplier or is billed for heating costs.
        subsidized = spm_unit("receives_housing_assistance", period) | (
            spm_unit.household("is_in_public_housing", period)
        )
        heat_in_rent = spm_unit("heat_expense_included_in_rent", period)
        pays_for_heat = spm_unit("has_heating_expense", period) | (
            heat_in_rent & ~subsidized
        )
        # 2025 manual Appendix E, denial code O: "Heats with Coal".
        heating_type = spm_unit("heating_type", period)
        heats_with_coal = heating_type == heating_type.possible_values.COAL
        return (
            (size > 0)
            & income_eligible
            & resource_eligible
            & pays_for_heat
            & ~heats_with_coal
        )
