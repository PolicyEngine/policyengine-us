from policyengine_us.model_api import *


class al_ssp_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Alabama SSP eligible"
    definition_period = MONTH
    defined_for = StateCode.AL
    reference = "https://admincode.legislature.state.al.us/api/chapter/660-2-4#page=9"

    def formula(person, period, parameters):
        is_ssi_eligible = person("is_ssi_eligible", period.this_year)
        receives_ssi = person("uncapped_ssi", period) > 0
        payment_category = person("al_ssp_payment_category", period)
        grandfathered = person("al_ssp_grandfathered", period)
        values = payment_category.possible_values
        in_qualifying_arrangement = payment_category != values.NONE
        requires_closed_cohort = payment_category == values.CEREBRAL_PALSY
        requires_waiver_and_snf = (
            (payment_category == values.IHC_LEVEL_A)
            | (payment_category == values.IHC_LEVEL_B)
            | (payment_category == values.FOSTER_CARE)
        )
        waiver_and_snf_qualified = person(
            "al_receives_elderly_disabled_medicaid_waiver", period
        ) & person("al_meets_snf_criteria", period)
        current_ssi_linked_eligibility = (
            is_ssi_eligible
            & receives_ssi
            & in_qualifying_arrangement
            & ~requires_closed_cohort
            & (~requires_waiver_and_snf | waiver_and_snf_qualified)
        )
        grandfathered_eligibility = grandfathered & in_qualifying_arrangement
        return current_ssi_linked_eligibility | grandfathered_eligibility
