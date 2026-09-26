from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.medicaid.income.medicaid_income_level import (
    medicaid_income_eligible,
)


class is_pregnant_for_medicaid_fc(Variable):
    value_type = bool
    entity = Person
    label = "Medicaid pregnant financial criteria"
    definition_period = YEAR
    reference = (
        # 42 CFR 435.116(b): pregnant women with household income at or below the
        # state's income standard.
        "https://www.law.cornell.edu/cfr/text/42/435.116",
        # WIC § 15832(a)(1)(B): California's Medi-Cal Access Program covers
        # household income "above 208 percent" but "not exceed[ing] 317
        # percent" of the FPL (213% and 322% after the 5 percentage point MAGI
        # disregard), so income exactly at the pregnancy Medi-Cal limit stays in
        # Medi-Cal. The section-level URL returns a version picker; this link
        # renders the full chapter text.
        "https://leginfo.legislature.ca.gov/faces/codes_displayText.xhtml?lawCode=WIC&division=9.&title=&part=3.3.&chapter=2.&article=",
    )

    def formula(person, period, parameters):
        ma = parameters(period).gov.hhs.medicaid.eligibility.categories.pregnant
        state = person.household("state_code_str", period)
        income_limit = ma.income_limit[state]
        return medicaid_income_eligible(person, period, parameters, income_limit)
