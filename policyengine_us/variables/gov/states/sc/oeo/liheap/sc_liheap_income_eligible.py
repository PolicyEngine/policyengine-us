from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class sc_liheap_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Income eligible for South Carolina LIHEAP"
    definition_period = YEAR
    defined_for = StateCode.SC
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/8624#b_2_B",
        # PDF pages 8,10
        "https://oeo.sc.gov/managedsites/prd/oeo/documents/2026%20LIHEAP%20State%20Plan.pdf#page=8",
        # PDF pages 8,10
        "https://liheapch.acf.gov/docs/2027/state-plans/SC_Plan_2027.pdf#page=8",
        "https://oeo.sc.gov/managedsites/prd/oeo/liheap.html",
    )

    def formula(spm_unit, period, parameters):
        # Plan items 2.1 and 3.1 set the same 60% of SMI threshold for the
        # heating and cooling components.
        p = parameters(period).gov.states.sc.oeo.liheap
        size = spm_unit("sc_liheap_household_size", period)
        income = spm_unit("sc_liheap_countable_income", period)
        limit = spm_unit("sc_liheap_income_limit", period)
        guideline = fpg(
            size,
            spm_unit.household("state_group_str", period),
            period,
            parameters,
            year_lag=p.eligibility.fpg_year_lag,
        )
        federal_floor = np.round(
            guideline * parameters(period).gov.hhs.liheap.fpg_floor, 2
        )
        return (size > 0) & ((income <= limit) | (income < federal_floor))
