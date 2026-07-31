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
        licensed_full_day = p.rates.licensed[location][provider_key][age_group][
            quality_key
        ][NEChildCareSubsidyRateUnit.FULL_DAY.name]
        exempt_family_daily = p.rates.license_exempt_family_home[location][unit_key]
        exempt_family_full_day = p.rates.license_exempt_family_home[location][
            NEChildCareSubsidyRateUnit.FULL_DAY.name
        ]

        paid_days = person("ne_child_care_subsidy_paid_days", period)
        absence_days = clip(
            person("ne_child_care_subsidy_approved_absence_days", period),
            0,
            p.attendance.max_absence_days,
        )
        attending_days = max_(paid_days - absence_days, 0)
        # Nebraska prices each approved absence as one full-day unit,
        # independently of the child's ordinary authorized unit.
        licensed_monthly = (
            licensed_daily * attending_days + licensed_full_day * absence_days
        )
        exempt_family_monthly = (
            exempt_family_daily * attending_days + exempt_family_full_day * absence_days
        )
        members = person.spm_unit.members
        member_provider = members("ne_child_care_subsidy_provider_type", period)
        member_provider_eligible = members(
            "ne_child_care_subsidy_provider_eligible", period
        )
        member_in_home = (
            member_provider == NEChildCareSubsidyProviderType.LICENSE_EXEMPT_IN_HOME
        ) & member_provider_eligible
        member_hours = members("ne_child_care_subsidy_authorized_weekly_hours", period)
        # One in-home provider serves the family, so the base uses the
        # maximum concurrent authorization rather than a wage per child.
        in_home_hours = person.spm_unit.max(member_hours * member_in_home)
        in_home_monthly = (
            p.rates.license_exempt_in_home
            * in_home_hours
            * WEEKS_IN_YEAR
            / MONTHS_IN_YEAR
        )
        in_home_child_count = person.spm_unit.sum(member_in_home)
        in_home_base_per_child = np.zeros_like(in_home_monthly)
        has_in_home_children = in_home_child_count > 0
        in_home_base_per_child[has_in_home_children] = (
            in_home_monthly[has_in_home_children]
            / in_home_child_count[has_in_home_children]
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
                in_home_base_per_child,
                0,
            ],
            default=0,
        )

        special_needs = person("ne_dhhs_has_special_needs", period.this_year)
        approved = person("ne_child_care_subsidy_special_needs_rate_approved", period)
        special_increase = where(
            provider == NEChildCareSubsidyProviderType.LICENSE_EXEMPT_IN_HOME,
            in_home_monthly * p.special_needs.in_home_increase_per_child,
            base_rate * p.special_needs.max_increase,
        )
        special_increase = where(special_needs & approved, special_increase, 0)
        quality_reported = quality != NEChildCareSubsidyQualityTier.NONE
        licensed = (provider == NEChildCareSubsidyProviderType.HOME_I_II) | (
            provider == NEChildCareSubsidyProviderType.CENTER
        )
        return (base_rate + special_increase) * (~licensed | quality_reported)
