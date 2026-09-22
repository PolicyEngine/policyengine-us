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
        # WIC § 15832(a)(1)(B): California's Medi-Cal Access Program begins above
        # the pregnancy Medi-Cal limit, so income exactly at the limit stays in
        # Medi-Cal.
        "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=WIC&sectionNum=15832.",
    )

    def formula(person, period, parameters):
        ma = parameters(period).gov.hhs.medicaid.eligibility.categories.pregnant
        state = person.household("state_code_str", period)
        income_limit = ma.income_limit[state]
        return medicaid_income_eligible(person, period, parameters, income_limit)
