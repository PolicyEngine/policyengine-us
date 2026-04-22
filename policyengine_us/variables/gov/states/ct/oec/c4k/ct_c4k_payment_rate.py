from policyengine_us.model_api import *


class ct_c4k_payment_rate(Variable):
    value_type = float
    entity = Person
    unit = USD
    definition_period = MONTH
    defined_for = "ct_c4k_eligible_child"
    label = "Connecticut Care 4 Kids weekly payment rate per child"
    reference = "https://www.ctoec.org/care-4-kids/c4k-providers/c4k-rates/"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ct.oec.c4k
        provider_type = person("ct_c4k_provider_type", period)
        types = provider_type.possible_values
        care_level = person("ct_c4k_care_level", period)
        region = person.household("ct_c4k_region", period)
        age_group = person("ct_c4k_age_group", period)

        weekly_rate = select(
            [
                provider_type == types.CENTER,
                provider_type == types.FAMILY,
                provider_type == types.RELATIVE,
                provider_type == types.RECREATIONAL,
            ],
            [
                p.rate.center[care_level][region][age_group],
                p.rate.family[care_level][region][age_group],
                p.rate.relative[care_level][region][age_group],
                p.rate.recreational[care_level][region][age_group],
            ],
            default=p.rate.center[care_level][region][age_group],
        )

        is_disabled = person("is_disabled", period.this_year)
        special_needs_add = where(is_disabled, p.special_needs_supplement, 0)
        is_accredited = person("ct_c4k_provider_accredited", period)
        accreditation_add = where(is_accredited, p.accreditation_bonus, 0)
        return weekly_rate * (1 + special_needs_add + accreditation_add)
