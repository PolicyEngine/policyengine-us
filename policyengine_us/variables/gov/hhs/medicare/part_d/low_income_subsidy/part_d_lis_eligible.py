from policyengine_us.model_api import *


class part_d_lis_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for the Medicare Part D low-income subsidy"
    documentation = (
        "A Medicare enrollee living in the 50 states or the District of "
        "Columbia who is deemed eligible or meets the income and resource "
        "tests. Before 2024 people with income from 135% to 150% of the "
        "poverty guideline, or resources between the lower and higher "
        "limits, got a partial subsidy; this covers both."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/1395w-114#a_3",
        "https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-423/subpart-P/section-423.773",
        "https://www.ecfr.gov/current/title-20/chapter-III/part-418/subpart-D/section-418.3101",
    )
    defined_for = "medicare_enrolled"

    def formula(person, period, parameters):
        p = parameters(period).gov.hhs.medicare.part_d.low_income_subsidy.eligibility
        state_code = person.household("state_code_str", period)
        in_state = ~np.isin(state_code, p.ineligible_jurisdictions)
        deemed = person("part_d_lis_deemed_eligible", period)
        income_eligible = person("part_d_lis_income_eligible", period)
        resource_eligible = person("part_d_lis_resource_eligible", period)
        return in_state & (deemed | (income_eligible & resource_eligible))
