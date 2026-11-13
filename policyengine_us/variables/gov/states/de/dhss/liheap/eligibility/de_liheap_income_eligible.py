from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class de_liheap_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Meets the Delaware LIHEAP household and income test"
    defined_for = StateCode.DE
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/8624#b_2_B",
        "https://liheapch.acf.gov/docs/2026/state-plans/DE_Plan_2026.pdf#page=9",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period)
        size = spm_unit("de_liheap_household_size", period)
        income = spm_unit("de_liheap_countable_income", period)
        limit = spm_unit("de_liheap_income_limit", period)
        guideline = fpg(
            max_(size, 1),
            spm_unit.household("state_group_str", period),
            period,
            parameters,
            year_lag=p.gov.states.de.dhss.liheap.eligibility.fpg_year_lag,
        )
        federal_floor = np.round(guideline * p.gov.hhs.liheap.fpg_floor, 2)
        return (size > 0) & ((income <= limit) | (income < federal_floor))
