from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class ct_ceap_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Connecticut CEAP income eligible without categorical receipt"
    definition_period = YEAR
    defined_for = StateCode.CT
    reference = (
        "https://portal.ct.gov/dss/-/media/departments-and-agencies/dss/winter-heating-assistance/09012026/ffy-27-liheap-allocation-plan.pdf#page=7",
        "https://www.law.cornell.edu/uscode/text/42/8624#b_2_B",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ct.dss.ceap.payment
        p_hhs = parameters(period).gov.hhs.liheap
        size = spm_unit("ct_ceap_household_size", period)
        state_group = spm_unit.household("state_group_str", period)
        guideline = fpg(size, state_group, period, parameters, year_lag=p.fpg_year_lag)
        # Preserve the published ceiling and the strict federal protection
        # where the SMI limit is lower for large households.
        floor = np.round(guideline * p_hhs.fpg_floor, 2)
        income = spm_unit("ct_ceap_countable_income", period)
        limit = spm_unit("ct_ceap_income_limit", period)
        return (income <= limit) | (income < floor)
