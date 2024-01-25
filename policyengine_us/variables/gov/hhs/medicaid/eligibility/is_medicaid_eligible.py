from policyengine_us.model_api import *


class is_medicaid_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for Medicaid"
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/1396a#a_10"
        "https://www.kff.org/racial-equity-and-health-policy/fact-sheet/key-facts-on-health-coverage-of-immigrants"
    )

    def formula(person, period, parameters):
        category = person("medicaid_category", period)
        categorically_eligible = category != category.possible_values.NONE
        istatus = person("immigration_status", period)
        undocumented = istatus == istatus.possible_values.UNDOCUMENTED
        state = person.household("state_code_str", period)
        p = parameters(period).gov.hhs.medicaid.eligibility
        state_covers_undocumented = p.undocumented_immigrant[state].astype(
            bool
        )
        immigration_status_eligible = (
            ~undocumented | undocumented & state_covers_undocumented
        )
        return categorically_eligible & immigration_status_eligible
