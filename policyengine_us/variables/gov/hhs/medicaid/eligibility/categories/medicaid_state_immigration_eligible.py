from policyengine_us.model_api import *


class medicaid_state_immigration_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible person for medicaid based on the state immigration rules"
    documentation = "Qualifies for Medicaid due to extended coverage for undocumented immigrants."
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/42/1396a#f"

    def formula(person, period, parameters):
        state = person.household("state_code_str", period)
        p = parameters(period).gov.hhs.medicaid.eligibility
        return p.immigration[state]
