from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.ne.dhhs.child_care_subsidy.ne_child_care_subsidy_age_group import (
    NEChildCareSubsidyAgeGroup,
)
from policyengine_us.variables.gov.states.ne.dhhs.child_care_subsidy.ne_child_care_subsidy_provider_type import (
    NEChildCareSubsidyProviderType,
)
from policyengine_us.variables.gov.states.ne.dhhs.child_care_subsidy.ne_child_care_subsidy_quality_tier import (
    NEChildCareSubsidyQualityTier,
)
from policyengine_us.variables.gov.states.ne.dhhs.child_care_subsidy.ne_child_care_subsidy_rate_unit import (
    NEChildCareSubsidyRateUnit,
)


class ne_child_care_subsidy_maximum_provider_rate(Variable):
    value_type = float
    entity = Person
    unit = USD
    definition_period = MONTH
    label = "Nebraska Child Care Subsidy maximum monthly provider rate"
    defined_for = "ne_child_care_subsidy_provider_eligible"
    reference = (
        "https://dhhs.ne.gov/Child%20Care%20Documents/Subsidy-Rates.pdf#page=1",
        "https://dhhs.ne.gov/Documents/CC-Subsidy-Provider-Booklet.pdf#page=31",
        "https://dhhs.ne.gov/Guidance%20Docs/Title%20392%20-%20Child%20Care%20Subsidy.pdf#page=10",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ne.dhhs.child_care_subsidy
        provider = person("ne_child_care_subsidy_provider_type", period)
        age_group = person("ne_child_care_subsidy_age_group", period)
        quality = person("ne_child_care_subsidy_quality_tier", period)
        rate_unit = person("ne_child_care_subsidy_rate_unit", period)
        location = person.household("ne_child_care_subsidy_location", period.this_year)

        provider_key = where(
            provider == NEChildCareSubsidyProviderType.CENTER,
            NEChildCareSubsidyProviderType.CENTER.name,
            NEChildCareSubsidyProviderType.HOME_I_II.name,
        )
        quality_key = select(
            [
                quality == NEChildCareSubsidyQualityTier.BASE,
                quality == NEChildCareSubsidyQualityTier.ACCREDITED_STEP_3,
                quality == NEChildCareSubsidyQualityTier.STEP_4,
                quality == NEChildCareSubsidyQualityTier.STEP_5,
                quality == NEChildCareSubsidyQualityTier.NONE,
            ],
            [
                NEChildCareSubsidyQualityTier.BASE.name,
                NEChildCareSubsidyQualityTier.ACCREDITED_STEP_3.name,
                NEChildCareSubsidyQualityTier.STEP_4.name,
                NEChildCareSubsidyQualityTier.STEP_5.name,
                NEChildCareSubsidyQualityTier.BASE.name,
            ],
            default=NEChildCareSubsidyQualityTier.BASE.name,
        )
        unit_key = select(
            [
                rate_unit == NEChildCareSubsidyRateUnit.PARTIAL_DAY,
                rate_unit == NEChildCareSubsidyRateUnit.FULL_DAY,
                rate_unit == NEChildCareSubsidyRateUnit.FULL_PLUS_PARTIAL,
                rate_unit == NEChildCareSubsidyRateUnit.HOUR,
                rate_unit == NEChildCareSubsidyRateUnit.NONE,
            ],
            [
                NEChildCareSubsidyRateUnit.PARTIAL_DAY.name,
                NEChildCareSubsidyRateUnit.FULL_DAY.name,
                NEChildCareSubsidyRateUnit.FULL_PLUS_PARTIAL.name,
                NEChildCareSubsidyRateUnit.PARTIAL_DAY.name,
                NEChildCareSubsidyRateUnit.PARTIAL_DAY.name,
            ],
            default=NEChildCareSubsidyRateUnit.PARTIAL_DAY.name,
        )
        licensed_daily = p.rates.licensed[location][provider_key][age_group][
            quality_key
        ][unit_key]
        exempt_family_daily = p.rates.license_exempt_family_home[location][unit_key]

        paid_days = person("ne_child_care_subsidy_paid_days", period)
        authorized_hours = person(
            "ne_child_care_subsidy_authorized_weekly_hours", period
        )
        licensed_monthly = licensed_daily * paid_days
        exempt_family_monthly = exempt_family_daily * paid_days
        in_home_monthly = (
            p.rates.license_exempt_in_home
            * authorized_hours
            * WEEKS_IN_YEAR
            / MONTHS_IN_YEAR
        )
        base_rate = select(
            [
                provider == NEChildCareSubsidyProviderType.HOME_I_II,
                provider == NEChildCareSubsidyProviderType.CENTER,
                provider == NEChildCareSubsidyProviderType.LICENSE_EXEMPT_FAMILY_HOME,
                provider == NEChildCareSubsidyProviderType.LICENSE_EXEMPT_IN_HOME,
                provider == NEChildCareSubsidyProviderType.NONE,
            ],
            [
                licensed_monthly,
                licensed_monthly,
                exempt_family_monthly,
                in_home_monthly,
                0,
            ],
            default=0,
        )

        special_needs = person("ne_dhhs_has_special_needs", period.this_year)
        approved = person("ne_child_care_subsidy_special_needs_rate_approved", period)
        special_rate = where(
            provider == NEChildCareSubsidyProviderType.LICENSE_EXEMPT_IN_HOME,
            p.special_needs.in_home_increase_per_child,
            p.special_needs.max_increase,
        )
        multiplier = where(special_needs & approved, 1 + special_rate, 1)
        return base_rate * multiplier
