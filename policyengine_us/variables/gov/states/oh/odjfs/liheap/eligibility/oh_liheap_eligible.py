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
        "https://dam.assets.ohio.gov/image/upload/v1769700600/development.ohio.gov/individual/energyassistance/DETAILED_MODEL_PLAN_LIHEAP__10_01_2025.pdf#page=8",
        # Section E-4: heat-in-rent bills need not be in a member's name for HEAP.
        "https://irp.cdn-website.com/aa88b0b1/files/uploaded/2022-24%20ATTACHMENT%202022-2023%20EAP%20Guidelines%20%281%29.pdf#page=12",
        "https://www.law.cornell.edu/uscode/text/42/8624",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.oh.odjfs.liheap.eligibility
        p_hhs = parameters(period).gov.hhs.liheap
        size = spm_unit("oh_liheap_household_size", period)
        income = spm_unit("oh_liheap_countable_income", period)
        limit = spm_unit("oh_liheap_income_limit", period)
        guideline = fpg(
            max_(size, 1),
            spm_unit.household("state_group_str", period),
            period,
            parameters,
            year_lag=p.fpg_year_lag,
        )
        # 42 U.S.C. 8624(b)(2)(B) bars excluding a household on income below
        # 110% of the poverty guideline; Ohio's 60% SMI limit falls below that
        # floor from household size 17 in 2025-2027.
        income_eligible = (income <= limit) | (income < p_hhs.fpg_floor * guideline)
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
        # The model follows the Guidelines for unsubsidized tenants and the
        # plan and application for subsidized ones.
        pays_electricity = spm_unit("electricity_expense", period) > 0
        responsible = (spm_unit("heating_expense", period) > 0) | (
            heat_in_rent & (~subsidized | pays_electricity)
        )
        heating_type = spm_unit("heating_type", period)
        fuel = heating_type.possible_values
        # No categorical income bypass or asset test. Existing inputs cannot
        # identify every excluded institution, boarding house, or legal fixture.
        return (size > 0) & income_eligible & responsible & (heating_type != fuel.NONE)
