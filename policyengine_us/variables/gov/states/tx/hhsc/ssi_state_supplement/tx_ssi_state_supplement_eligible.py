from policyengine_us.model_api import *


class tx_ssi_state_supplement_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Texas SSI State Supplement eligible"
    definition_period = MONTH
    defined_for = StateCode.TX
    reference = (
        "https://statutes.capitol.texas.gov/Docs/HR/htm/HR.32.htm",
        "https://www.hhs.texas.gov/handbooks/medicaid-elderly-people-disabilities-handbook/h-6000-co-payment-ssi-cases",
        "https://www.hhs.texas.gov/handbooks/medicaid-elderly-people-disabilities-handbook/h-1500-personal-needs-allowance",
    )

    def formula(person, period, parameters):
        # MEPD Handbook H-1500: "SSI recipients who live in an institutional
        # setting and receive the $30 reduced federal benefit receive a state
        # supplement." H-6000 gives a couple in a facility the $60 couple
        # standard, so each spouse receives the reduced benefit and qualifies.
        receives_ssi = (person("ssi", period) > 0) | person("receives_ssi", period)
        in_facility = person("is_in_medicaid_facility", period)
        return receives_ssi & in_facility
