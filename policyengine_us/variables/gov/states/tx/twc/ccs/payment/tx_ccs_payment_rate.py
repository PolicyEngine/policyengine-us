from policyengine_us.model_api import *


class tx_ccs_payment_rate(Variable):
    value_type = float
    entity = Person
    label = "Texas Child Care Services (CCS) payment amount"
    unit = USD
    definition_period = MONTH
    defined_for = "tx_ccs_eligible_child"
    reference = "https://www.twc.texas.gov/sites/default/files/ccel/docs/bcy25-board-max-provider-payment-rates-4-age-groups-twc.pdf#page=9"

    def formula(person, period, parameters):
        # Get the household's workforce board region
        household = person.household
        region = household("tx_ccs_workforce_board_region", period)

        # Get the payment parameters
        p = parameters(period).gov.states.tx.twc.ccs.payment

        # Get the provider characteristics
        provider_type = person("tx_ccs_provider_type", period)
        provider_rating = person("tx_ccs_provider_rating", period)
        age_category = person("tx_ccs_child_age_category", period)
        care_schedule = person("tx_ccs_care_schedule", period)

        # Calculate monthly payment based on region-specific rates
        attending_days_per_month = person(
            "childcare_attending_days_per_month", period.this_year
        )
        return (
            p.rates[region][provider_type][provider_rating][age_category][
                care_schedule
            ]
            * attending_days_per_month
        )
