from policyengine_us.model_api import *


class ira_active_participant(Variable):
    value_type = bool
    entity = Person
    label = "Active participant in an employer retirement plan for IRA deductions"
    definition_period = YEAR
    default_value = False
    documentation = (
        "Whether this person was an active participant for any part of a plan "
        "year ending within the tax year in a plan covered by section 219(g)(5), "
        "including defined benefit, 401(a), 403(a), 403(b), SEP and SIMPLE plans. "
        "By default, positive traditional or Roth 401(k) or 403(b) contributions "
        "or self-employed pension contributions establish this person's own "
        "coverage. An explicitly supplied value always overrides this default, "
        "including false. Supply defined-benefit coverage and coverage from "
        "employer contributions not represented by these amounts explicitly, "
        "generally using Form W-2 box 13. Do not include a spouse's coverage or "
        "participation solely in a 457(b) plan. Apply the reserve and volunteer "
        "firefighter exceptions in section 219(g)(6) through an explicit input. "
        "When supplying coverage inputs, supply every relevant person's value: "
        "core stores a population input array and defaults omitted rows to false."
    )
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/219#g_5",
        "https://www.irs.gov/publications/p590a",
        "https://www.irs.gov/instructions/iw2w3",
    )

    def formula(person, period, parameters):
        # Section 219(g)(5) excludes participation solely in a 457(b) plan.
        # Check each amount separately so a negative input cannot cancel
        # positive contributions to another qualifying plan.
        return (
            (person("traditional_401k_contributions", period) > 0)
            | (person("roth_401k_contributions", period) > 0)
            | (person("traditional_403b_contributions", period) > 0)
            | (person("roth_403b_contributions", period) > 0)
            | (person("self_employed_pension_contributions", period) > 0)
        )
