from policyengine_us.model_api import *
from policyengine_us.parameters.gov.states.tx.twc.ccs.payment.rates_v2 import (
    bcy26_rates,
)


class tx_ccs_payment_rate(Variable):
    value_type = float
    entity = Person
    label = "Texas Child Care Services (CCS) payment amount"
    unit = USD
    definition_period = MONTH
    defined_for = "tx_ccs_eligible_child"
    reference = (
        "https://www.twc.texas.gov/sites/default/files/ccel/docs/bcy25-board-max-provider-payment-rates-4-age-groups-twc.pdf#page=9",
        "https://www.twc.texas.gov/sites/default/files/ccel/docs/bcy26-board-max-provider-payment-rates-8-age-groups-twc.pdf",
    )

    def formula(person, period, parameters):
        household = person.household
        region = household("tx_ccs_workforce_board_region", period)

        p = parameters(period).gov.states.tx.twc.ccs.payment

        provider_type = person("tx_ccs_provider_type", period)
        provider_rating = person("tx_ccs_provider_rating", period)
        age_category = person("tx_ccs_child_age_category", period)
        care_schedule = person("tx_ccs_care_schedule", period)

        uses_expanded = p.uses_expanded_age_groups

        attending_days_per_month = person(
            "childcare_attending_days_per_month", period.this_year
        )

        if uses_expanded:
            daily_rate = _lookup_expanded_rate(
                region,
                provider_type,
                provider_rating,
                age_category,
                care_schedule,
            )
        else:
            daily_rate = p.rates[region][provider_type][
                provider_rating
            ][age_category][care_schedule]

        return daily_rate * attending_days_per_month


def _lookup_expanded_rate(
    region, provider_type, provider_rating, age_category, care_schedule
):
    @np.vectorize
    def _lookup(r, pt, pr, ac, cs):
        return (
            bcy26_rates.get(r, {})
            .get(pt, {})
            .get(pr, {})
            .get(ac, {})
            .get(cs, 0.0)
        )

    return _lookup(
        region.decode_to_str(),
        provider_type.decode_to_str(),
        provider_rating.decode_to_str(),
        age_category.decode_to_str(),
        care_schedule.decode_to_str(),
    )
