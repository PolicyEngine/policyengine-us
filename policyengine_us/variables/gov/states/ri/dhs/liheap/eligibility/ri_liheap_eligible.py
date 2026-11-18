from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class ri_liheap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Rhode Island LIHEAP regular heating eligibility"
    defined_for = StateCode.RI
    reference = (
        # PDF pages 5-6, 12
        "https://ripuc.ri.gov/eventsactions/docket/4290-DHS-DR-PUC%203-6%20attachment%20LIHEAP%20Manual%202020%20-%20Final.pdf#page=5",
        # PDF pages 8, 45
        "https://liheapch.acf.gov/docs/2026/state-plans/RI_Plan_2026.pdf#page=8",
        "https://www.law.cornell.edu/uscode/text/42/8624#b_2_B",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ri.dhs.liheap
        size = spm_unit("ri_liheap_household_size", period)
        income = spm_unit("ri_liheap_income", period)
        limit = spm_unit("ri_liheap_income_limit", period)
        # 42 U.S.C. 8624(b)(2)(B) bars excluding a household on income below 110%
        # of the poverty guideline. The 60% SMI limit falls below that floor from
        # household size 23 in 2026 and 2027 (21 and 19 in the 2025 and 2024
        # backfills).
        p_hhs = parameters(period).gov.hhs.liheap
        state_group = spm_unit.household("state_group_str", period)
        guideline = fpg(size, state_group, period, parameters, year_lag=p.fpg_year_lag)
        floor = np.round(guideline * p_hhs.fpg_floor, 2)
        income_eligible = (income <= limit) | (income < floor)
        heat_in_rent = spm_unit("heat_expense_included_in_rent", period)
        subsidized = spm_unit("receives_housing_assistance", period) | (
            spm_unit.household("is_in_public_housing", period)
        )
        primary_obligation = spm_unit("has_heating_expense", period) | (
            spm_unit("heating_expense", period) > 0
        )
        separate_electric_bill = spm_unit("pre_subsidy_electricity_expense", period) > 0
        # Reported obligations and rental terms are assumed verified.
        # Manual II.B (page 6): "Subsidized renters with no utility burden are
        # ineligible for this program." FY2026 plan item 2.3 (page 8) answers No to
        # differing policies for "Renters Living in subsidized housing?". This
        # follows the manual.
        energy_burden = where(
            heat_in_rent, ~subsidized | separate_electric_bill, primary_obligation
        )
        # Electric heat in unsubsidized rent with no electric bill (blank row G
        # cell), and COAL, OTHER and SOLAR outside heat in rent, stay eligible but
        # have no matrix amount, so ri_liheap pays $0.
        heating_type = spm_unit("heating_type", period)
        return (
            (size > 0)
            & income_eligible
            & energy_burden
            & (heating_type != heating_type.possible_values.NONE)
        )
