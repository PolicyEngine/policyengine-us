from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.nd.dhs.ccap.rates.nd_ccap_time_category import (
    NDCCAPTimeCategory,
)
from policyengine_us.variables.gov.states.nd.dhs.ccap.rates.nd_ccap_provider_qris_step import (
    NDCCAPProviderQRISStep,
)


class nd_ccap_state_max_rate(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "North Dakota CCAP state maximum rate per child"
    definition_period = MONTH
    defined_for = "nd_ccap_eligible_child"
    reference = "https://www.nd.gov/dhs/policymanuals/40028/40028.htm"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.nd.dhs.ccap.rates
        provider_type = person("nd_ccap_provider_type", period)
        age_group = person("nd_ccap_age_group", period)
        time_category = person("nd_ccap_time_category", period)
        full_time_rate = p.full_time[provider_type][age_group]
        part_time_rate = p.part_time[provider_type][age_group]
        base_rate = where(
            time_category == NDCCAPTimeCategory.FULL_TIME,
            full_time_rate,
            part_time_rate,
        )
        # A child who meets the definition of disability and attends a provider
        # with a QRIS rating of step 2 or higher receives an additional 10% of
        # the state maximum rate (400-28-100-30). is_disabled proxies the
        # required written special-needs verification; the manual's reference
        # to KRS definitions is a copy-paste artifact, so we cite the North
        # Dakota manual. The 10% raises the rate ceiling, so it folds inside
        # the expense cap applied in nd_ccap_base_subsidy.
        is_disabled = person("is_disabled", period.this_year)
        qris_step = person("nd_ccap_provider_qris_step", period)
        step_2_or_higher = (
            (qris_step == NDCCAPProviderQRISStep.STEP_2)
            | (qris_step == NDCCAPProviderQRISStep.STEP_3)
            | (qris_step == NDCCAPProviderQRISStep.STEP_4)
        )
        special_needs_multiplier = where(
            is_disabled & step_2_or_higher, p.special_needs_multiplier, 1
        )
        return base_rate * special_needs_multiplier
