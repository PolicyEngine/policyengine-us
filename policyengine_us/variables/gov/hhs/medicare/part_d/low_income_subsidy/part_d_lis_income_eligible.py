from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class part_d_lis_income_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Income eligible for the Medicare Part D low-income subsidy"
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/1395w-114#a_3_A_ii",
        "https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-423/subpart-P/section-423.773#p-423.773(a)(1)",
        "https://secure.ssa.gov/poms.nsf/lnx/0603020055",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.hhs.medicare.part_d.low_income_subsidy.eligibility
        family_size = person("part_d_lis_family_size", period)
        state_group = person.household("state_group_str", period)
        income_limit = p.income_limit * fpg(
            family_size, state_group, period, parameters
        )
        return person("part_d_lis_countable_income", period) < income_limit
