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
        # supplement." H-6000: such a resident "remains eligible for SSI if
        # their countable income does not exceed the SSI reduced standard
        # payment amount", so countable income equal to it, with a $0 federal
        # payment, still qualifies. The test is against the reduced standard
        # itself, since this program identifies residents through
        # is_in_medicaid_facility rather than the SSI living arrangement. For
        # a couple in a facility, SSI's couple computation gives each spouse
        # half the couple's countable income, held to their $30 half of the
        # $60 couple standard (H-6000).
        p = parameters(period).gov.ssa.ssi
        countable_income = person("ssi_countable_income", period)
        within_reduced_standard = countable_income <= p.amount.institutional.individual
        eligible_for_ssi = (
            person("is_ssi_eligible", period)
            & person("takes_up_ssi_if_eligible", period.this_year)
            & within_reduced_standard
            & ~p.abolish_ssi
        )
        receives_ssi = person("receives_ssi", period)
        in_facility = person("is_in_medicaid_facility", period)
        return (eligible_for_ssi | receives_ssi) & in_facility
