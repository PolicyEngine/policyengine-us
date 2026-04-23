from policyengine_us.model_api import *


class tx_ssi_state_supplement_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Texas SSI State Supplement eligible"
    definition_period = YEAR
    defined_for = StateCode.TX
    reference = (
        "https://statutes.capitol.texas.gov/Docs/HR/htm/HR.32.htm",
        "https://www.hhs.texas.gov/handbooks/medicaid-elderly-people-disabilities-handbook/h-6000-co-payment-ssi-cases",
    )

    def formula(person, period, parameters):
        ssi_eligible = person("is_ssi_eligible_individual", period)
        in_facility = person("is_in_medicaid_facility", period)
        return ssi_eligible & in_facility
