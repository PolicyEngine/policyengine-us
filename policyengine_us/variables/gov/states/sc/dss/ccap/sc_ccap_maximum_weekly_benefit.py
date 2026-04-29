from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.sc.dss.ccap.sc_ccap_provider_type import (
    SCCCAPProviderType,
)


class sc_ccap_maximum_weekly_benefit(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "South Carolina CCAP maximum weekly benefit per child"
    definition_period = MONTH
    defined_for = "sc_ccap_eligible_child"
    reference = (
        "https://www.scchildcare.org/media/vwybydmg/child-care-scholarship-maximum-payments-allowed-ffy2023-pdf.pdf#page=1",
        "https://www.scchildcare.org/media/ubhdm1at/1-13-2025_policy-manual.pdf#page=183",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.sc.dss.ccap
        provider_type = person("sc_ccap_provider_type", period)
        time_category = person("sc_ccap_time_category", period)
        age_group = person("sc_ccap_age_group", period)
        geography = person.household("sc_ccap_geography", period.this_year)

        quality = person("sc_ccap_quality_level", period)
        reg_quality = person("sc_ccap_registered_quality_level", period)

        rates = p.rates
        # Centers, exempt centers, group homes, and licensed family homes
        # all use the same 4-dimensional breakdown:
        # time_category x quality_level x age_group x geography.
        center_rate = rates.center[time_category][quality][age_group][geography]
        exempt_center_rate = rates.exempt_center[time_category][quality][age_group][
            geography
        ]
        group_home_rate = rates.group_home[time_category][quality][age_group][geography]
        licensed_family_rate = rates.licensed_family_home[time_category][quality][
            age_group
        ][geography]
        # Registered family homes have a reduced quality scale (B+, B, C).
        registered_family_rate = rates.registered_family_home[time_category][
            reg_quality
        ][age_group][geography]
        # FFN has no quality level or geography dimension.
        ffn_rate = rates.ffn[time_category][age_group]

        base_rate = select(
            [
                provider_type == SCCCAPProviderType.CENTER,
                provider_type == SCCCAPProviderType.EXEMPT_CENTER,
                provider_type == SCCCAPProviderType.GROUP_HOME,
                provider_type == SCCCAPProviderType.LICENSED_FAMILY_HOME,
                provider_type == SCCCAPProviderType.REGISTERED_FAMILY_HOME,
                provider_type == SCCCAPProviderType.FFN,
            ],
            [
                center_rate,
                exempt_center_rate,
                group_home_rate,
                licensed_family_rate,
                registered_family_rate,
                ffn_rate,
            ],
        )

        # Apply provider-determined second child discount.
        # Per Policy Manual 5.11 (p.137), the discount applies per-facility
        # to all children except the youngest at that facility. We assume
        # all children use the same provider as a simplification.
        # Only children actually in care count for the youngest determination.
        discount_rate = person("sc_ccap_second_child_discount_rate", period)
        in_care = person("childcare_hours_per_week", period) > 0
        child_index = person("child_index", period.this_year)
        in_care_index = where(in_care, child_index, -1)
        max_in_care_index = person.spm_unit.max(in_care_index)
        is_not_youngest = in_care & (child_index < max_in_care_index)
        discounted_rate = where(
            is_not_youngest,
            base_rate * (1 - discount_rate),
            base_rate,
        )

        # Add surcharges for special needs and foster care children.
        is_disabled = person("is_disabled", period.this_year)
        is_foster = person("is_in_foster_care", period)
        special_needs_surcharge = where(is_disabled, p.surcharge.special_needs, 0)
        foster_surcharge = where(is_foster, p.surcharge.foster_care, 0)

        rate = discounted_rate + special_needs_surcharge + foster_surcharge

        # Head Start pathway only covers the enrolled child (Section 2.15).
        # Non-Head-Start children need the family to qualify through
        # standard or protective pathway.
        is_head_start = person("is_enrolled_in_head_start", period.this_year)
        income_eligible = person.spm_unit("sc_ccap_income_eligible", period)
        asset_eligible = person.spm_unit("is_ccdf_asset_eligible", period.this_year)
        activity_eligible = person.spm_unit("sc_ccap_activity_eligible", period)
        protective = person.spm_unit("sc_ccap_protective_services", period)
        standard_or_protective = (
            income_eligible & asset_eligible & (activity_eligible | protective)
        )
        child_covered = is_head_start | standard_or_protective
        in_care = person("childcare_hours_per_week", period) > 0

        return where(child_covered & in_care, rate, 0)
