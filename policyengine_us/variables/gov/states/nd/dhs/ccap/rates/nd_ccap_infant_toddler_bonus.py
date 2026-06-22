from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.nd.dhs.ccap.rates.nd_ccap_provider_qris_step import (
    NDCCAPProviderQRISStep,
)
from policyengine_us.variables.gov.states.nd.dhs.ccap.rates.nd_ccap_provider_type import (
    NDCCAPProviderType,
)


class nd_ccap_infant_toddler_bonus(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "North Dakota CCAP infant/toddler bonus per child"
    definition_period = MONTH
    defined_for = "nd_ccap_eligible_child"
    reference = (
        "https://www.hhs.nd.gov/ec-news/child-care-assistance-program-ccap-updates-2026"
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.nd.dhs.ccap.rates
        # The infant/toddler bonus is a flat per-child provider payment paid to
        # licensed, tribally licensed, or military licensed providers rated at
        # QRIS step 2 or higher, for all infants and toddlers in care
        # (400-28-100-30; 2026 CCAP updates). The bonus is additive: it is not
        # capped at the family's billed expenses and not reduced by the
        # co-payment. The parameter is zero for preschool and school-age
        # children, so the age filter is handled by the lookup.
        age_group = person("nd_ccap_age_group", period)
        bonus_amount = p.infant_toddler_bonus[age_group]
        qris_step = person("nd_ccap_provider_qris_step", period)
        step_2_or_higher = (
            (qris_step == NDCCAPProviderQRISStep.STEP_2)
            | (qris_step == NDCCAPProviderQRISStep.STEP_3)
            | (qris_step == NDCCAPProviderQRISStep.STEP_4)
        )
        # Approved relatives are not licensed providers and do not receive the
        # licensed-provider bonus.
        provider_type = person("nd_ccap_provider_type", period)
        is_licensed_provider = provider_type != NDCCAPProviderType.APPROVED_RELATIVE
        return bonus_amount * step_2_or_higher * is_licensed_provider
