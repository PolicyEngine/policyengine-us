from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class oh_liheap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Ohio HEAP eligibility"
    defined_for = StateCode.OH
    reference = (
        "https://www.clevelandohio.gov/sites/clevelandohio/files/aging/Home%20repair%20Applications/2025-2026_HEAP_application_B_W.pdf#page=1",
        # FY2026 plan item 2.3 (renters) and Assurance 2 (the 110% floor).
        # PDF pages 8, 48
        "https://dam.assets.ohio.gov/image/upload/v1769700600/development.ohio.gov/individual/energyassistance/DETAILED_MODEL_PLAN_LIHEAP__10_01_2025.pdf#page=8",
        # FY2027 plan, revision 1: item 2.3 (renters) and Assurance 2.
        # PDF pages 9, 50
        "https://dam.assets.ohio.gov/image/upload/jfs.ohio.gov/Energy%20and%20Community%20Assistance/DETAILED_MODEL_PLAN_LIHEAP__10_01_2026.pdf#page=9",
        # Section E-4: heat-in-rent bills need not be in a member's name for HEAP.
        "https://irp.cdn-website.com/aa88b0b1/files/uploaded/2022-24%20ATTACHMENT%202022-2023%20EAP%20Guidelines%20%281%29.pdf#page=12",
        "https://www.law.cornell.edu/uscode/text/42/8624#b_2_B",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.oh.odjfs.liheap.eligibility
        p_hhs = parameters(period).gov.hhs.liheap
        size = spm_unit("oh_liheap_household_size", period)
        income = spm_unit("oh_liheap_countable_income", period)
        limit = spm_unit("oh_liheap_income_limit", period)
        # 42 U.S.C. 8624(b)(2)(B) bars excluding a household on income below 110%
        # of the poverty guideline. The 60% SMI limit falls below that floor from
        # household size 17 in 2025 to 2027.
        state_group = spm_unit.household("state_group_str", period)
        guideline = fpg(size, state_group, period, parameters, year_lag=p.fpg_year_lag)
        floor = np.round(guideline * p_hhs.fpg_floor, 2)
        income_eligible = (income <= limit) | (income < floor)
        heat_in_rent = spm_unit("heat_expense_included_in_rent", period)
        subsidized = spm_unit("receives_housing_assistance", period) | (
            spm_unit.household("is_in_public_housing", period)
        )
        # Reported bills and rental terms approximate verified liability.
        # Guidelines E-4 (page 12): "For HEAP only, the utility bill does not
        # have to be in a household member's name (for example, heat included
        # in the rent ...)". FY2026 plan item 2.3 (page 8) makes tenants whose
        # electric bills are not in their name ineligible "unless they provide
        # verification that they pay all or a portion" of the electric bill.
        # The accepted FY2027 plan's item 2.3 (page 9) repeats that text; its
        # July 2026 draft said "utility bills" for renters with utilities
        # included in the rent. The model follows the Guidelines for
        # unsubsidized tenants and the plans and application for subsidized
        # ones.
        pays_electricity = spm_unit("electricity_expense", period) > 0
        responsible = (spm_unit("heating_expense", period) > 0) | (
            heat_in_rent & (~subsidized | pays_electricity)
        )
        heating_type = spm_unit("heating_type", period)
        fuel = heating_type.possible_values
        # No categorical income bypass or asset test. Existing inputs cannot
        # identify every excluded institution, boarding house, or legal fixture.
        return (size > 0) & income_eligible & responsible & (heating_type != fuel.NONE)
