from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.ne.dhhs.child_care_subsidy.ne_child_care_subsidy_provider_type import (
    NEChildCareSubsidyProviderType,
)
from policyengine_us.variables.gov.states.ne.dhhs.child_care_subsidy.ne_child_care_subsidy_quality_tier import (
    NEChildCareSubsidyQualityTier,
)
from policyengine_us.variables.gov.states.ne.dhhs.child_care_subsidy.ne_child_care_subsidy_rate_unit import (
    NEChildCareSubsidyRateUnit,
)


class ne_child_care_subsidy_provider_eligible(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "Nebraska Child Care Subsidy provider conditions met"
    defined_for = "ne_child_care_subsidy_eligible_child"
    reference = (
        "https://rules.nebraska.gov/api/fileStorage/GetAsByteArray/title-pdfs/Title_392.pdf/180#page=17",
        "https://dhhs.ne.gov/Child%20Care%20Documents/ACF-118%20CCDF%20FFY%202025-2027%20For%20Nebraska%20-%20APPROVED.pdf#page=47",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ne.dhhs.child_care_subsidy.provider
        provider = person("ne_child_care_subsidy_provider_type", period)
        quality = person("ne_child_care_subsidy_quality_tier", period)
        rate_unit = person("ne_child_care_subsidy_rate_unit", period)
        licensed = (provider == NEChildCareSubsidyProviderType.HOME_I_II) | (
            provider == NEChildCareSubsidyProviderType.CENTER
        )
        licensed_quality_reported = ~licensed | (
            quality != NEChildCareSubsidyQualityTier.NONE
        )
        in_home = provider == NEChildCareSubsidyProviderType.LICENSE_EXEMPT_IN_HOME
        special_needs = person("ne_dhhs_has_special_needs", period.this_year)
        enough_children = (
            person.spm_unit("ne_child_care_subsidy_eligible_child_count", period)
            >= p.in_home_min_children
        )
        in_home_condition = (
            ~in_home
            | special_needs
            | enough_children
            | person("ne_child_care_subsidy_in_home_approved", period)
        )
        daily_unit = (
            (rate_unit == NEChildCareSubsidyRateUnit.PARTIAL_DAY)
            | (rate_unit == NEChildCareSubsidyRateUnit.FULL_DAY)
            | (rate_unit == NEChildCareSubsidyRateUnit.FULL_PLUS_PARTIAL)
        )
        unit_compatible = where(
            in_home,
            rate_unit == NEChildCareSubsidyRateUnit.HOUR,
            daily_unit,
        )
        return (
            (provider != NEChildCareSubsidyProviderType.NONE)
            & (rate_unit != NEChildCareSubsidyRateUnit.NONE)
            & unit_compatible
            & licensed_quality_reported
            & in_home_condition
        )
