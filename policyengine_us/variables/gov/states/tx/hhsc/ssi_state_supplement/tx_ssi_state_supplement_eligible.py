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
        # supplement." H-6000: such a person "remains eligible for SSI if
        # their countable income does not exceed the SSI reduced standard
        # payment amount", including income equal to it and a $0 federal
        # payment (42 USC 1382(a)(1)(A): income "not more than" the rate).
        # H-6000 gives a couple in a facility the $60 couple standard, so
        # each spouse is assessed on their own half.
        eligible_for_ssi = (
            person("is_ssi_eligible", period)
            & person("takes_up_ssi_if_eligible", period.this_year)
            & (person("uncapped_ssi", period) >= 0)
        )
        receives_ssi = person("receives_ssi", period)
        in_facility = person("is_in_medicaid_facility", period)
        return (eligible_for_ssi | receives_ssi) & in_facility
