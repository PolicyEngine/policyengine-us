from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class ct_ceap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Connecticut CEAP basic or rental heating assistance"
    definition_period = YEAR
    defined_for = StateCode.CT
    reference = (
        # PDF pages 7,9,11,15
        "https://portal.ct.gov/dss/-/media/departments-and-agencies/dss/winter-heating-assistance/09012026/ffy-27-liheap-allocation-plan.pdf#page=7",
        "https://www.law.cornell.edu/uscode/text/42/8624#b_2_B",
    )

    def formula(spm_unit, period, parameters):
        size = spm_unit("ct_ceap_household_size", period)
        income = spm_unit("ct_ceap_countable_income", period)
        limit = spm_unit("ct_ceap_income_limit", period)
        categorical = spm_unit("ct_ceap_categorically_eligible", period)
        p = parameters(period).gov.states.ct.dss.ceap.payment
        p_hhs = parameters(period).gov.hhs.liheap
        state_group = spm_unit.household("state_group_str", period)
        guideline = fpg(size, state_group, period, parameters, year_lag=p.fpg_year_lag)
        # Preserve the published ceiling and the strict federal protection
        # where the SMI limit is lower for large households.
        floor = np.round(guideline * p_hhs.fpg_floor, 2)
        income_eligible = (income <= limit) | (income < floor) | categorical
        heat_in_rent = spm_unit("heat_expense_included_in_rent", period)
        expense = spm_unit("heating_expense", period)
        heating_type = spm_unit("heating_type", period)
        has_heat = heating_type != heating_type.possible_values.NONE
        # Subsidized renters are not independently excluded. Heat-in-rent covers
        # verified rental heating costs; landlord/account verification is assumed.
        return (size > 0) & income_eligible & (heat_in_rent | (expense > 0)) & has_heat
