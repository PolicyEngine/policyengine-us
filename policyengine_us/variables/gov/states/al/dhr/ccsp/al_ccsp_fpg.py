from policyengine_us.model_api import *


class al_ccsp_fpg(Variable):
    value_type = float
    entity = SPMUnit
    label = "Alabama CCSP monthly federal poverty guideline"
    definition_period = MONTH
    unit = USD
    defined_for = StateCode.AL
    reference = (
        "https://dhr.alabama.gov/wp-content/uploads/2024/01/Child-Care-Fact-Sheet-2024.pdf#page=1",
        "https://dhr.alabama.gov/wp-content/uploads/2026/06/CHILD-CARE-FACT-SHEET-Jun2026-1.pdf#page=1",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.al.dhr.ccsp.income
        size = spm_unit("spm_unit_size", period.this_year)
        # The fact sheets print one row for families of eight or more.
        capped_size = min_(size, p.max_family_size)
        state_group = spm_unit.household("state_group_str", period.this_year)
        # Alabama's fact sheets use the prior calendar year's HHS poverty
        # guidelines throughout the benefit year, since HHS publishes the new
        # guidelines in mid-January.
        p_fpg = parameters(period.last_year).gov.hhs.fpg
        annual_fpg = p_fpg.first_person[state_group] + p_fpg.additional_person[
            state_group
        ] * (capped_size - 1)
        return annual_fpg / MONTHS_IN_YEAR
