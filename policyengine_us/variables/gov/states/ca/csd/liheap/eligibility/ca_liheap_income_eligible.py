from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class ca_liheap_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "California LIHEAP income eligible"
    defined_for = StateCode.CA
    reference = (
        # PDF pages 6,9,184
        "https://www.csd.ca.gov/Shared%20Documents/2026-Final-LIHEAP-State-Plan.pdf#page=6",
        "https://www.law.cornell.edu/uscode/text/42/8624#b_2_B",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ca.csd.liheap.income
        p_hhs = parameters(period).gov.hhs.liheap
        size = spm_unit("ca_liheap_household_size", period)
        state_group = spm_unit.household("state_group_str", period)
        guideline = fpg(size, state_group, period, parameters, year_lag=p.fpg_year_lag)
        # The published SMI ceiling is below the federal protection for large
        # households. Preserve that ceiling and the statute's strict boundary.
        floor = np.round(guideline * p_hhs.fpg_floor, 2)
        income = spm_unit("ca_liheap_countable_income", period)
        limit = spm_unit("ca_liheap_income_limit", period)
        return (
            spm_unit("ca_liheap_categorically_eligible", period)
            | (income <= limit)
            | (income < floor)
        )
