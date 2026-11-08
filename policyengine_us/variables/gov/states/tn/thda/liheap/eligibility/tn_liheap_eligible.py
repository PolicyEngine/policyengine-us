from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class tn_liheap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Tennessee LIHEAP regular assistance eligibility"
    defined_for = StateCode.TN
    reference = (
        # PDF pages 8, 24, 32-33
        "https://dogvxws799i6n.cloudfront.net/wp-content/uploads/LIHEAP-2026-Policy-Manual-for-Tennessee.pdf#page=8",
        "https://liheapch.acf.gov/docs/2026/state-plans/TN_Plan_2026.pdf#page=8",
        "https://www.law.cornell.edu/uscode/text/42/8624#b_2_B",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.tn.thda.liheap.eligibility
        p_hhs = parameters(period).gov.hhs.liheap
        size = spm_unit("tn_liheap_household_size", period)
        income = spm_unit("tn_liheap_countable_income", period)
        limit = spm_unit("tn_liheap_income_limit", period)
        # 42 U.S.C. 8624(b)(2)(B) bars excluding a household on income below
        # 110% of the poverty guideline. The 60% SMI limit falls below that
        # floor from household size 15 in FY2026 (98,009 against 101,915).
        state_group = spm_unit.household("state_group_str", period)
        guideline = fpg(size, state_group, period, parameters, year_lag=p.fpg_year_lag)
        floor = np.round(guideline * p_hhs.fpg_floor, 2)
        income_eligible = (income <= limit) | (income < floor)
        # Section 2.18 bars applicants "who do not have an active energy
        # account", and Section 1.2 defines one as a current utility account
        # that reflects billing and usage. The one regular award is applied as
        # heating or cooling assistance, so a counted bill of any fuel meets
        # the test, including in a home without heating. Energy included in
        # the rent under a landlord/tenant agreement also qualifies (Section
        # 2.17). heating_type is a required input, so an unspecified fuel
        # qualifies only through heat in the rent. Subsidized tenants with a
        # bill in their name are processed without adjustment, so housing
        # assistance is no condition here.
        has_energy_cost = spm_unit("tn_liheap_energy_cost", period) > 0
        heating_type = spm_unit("heating_type", period)
        known_fuel = heating_type != heating_type.possible_values.UNSPECIFIED
        heat_in_rent = spm_unit("heat_expense_included_in_rent", period)
        responsible = (has_energy_cost & known_fuel) | heat_in_rent
        return (size > 0) & income_eligible & responsible
