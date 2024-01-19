from policyengine_us.model_api import *


class medicaid_state_immigration_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible undocumented immigrant for medicaid based on the state eligiblity rules"
    documentation = "Qualifies for Medicaid due to extended state coverage for undocumented immigrants."
    definition_period = YEAR
    reference = "https://files.kff.org/attachment/Table-3-State-Adoption-of-Options-to-Cover-Immigrant-Populations-January-2021.pdf"

    def formula(person, period, parameters):
        state = person.household("state_code_str", period)
        p = parameters(period).gov.hhs.medicaid.eligibility
        return p.undocumented_immigrant[state]
