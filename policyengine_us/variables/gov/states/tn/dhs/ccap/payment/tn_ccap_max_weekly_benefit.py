from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.tn.dhs.ccap.tn_ccap_provider_type import (
    TNCCAPProviderType,
)
from policyengine_us.variables.gov.states.tn.dhs.ccap.tn_ccap_age_category import (
    TNCCAPAgeCategory,
)


class tn_ccap_max_weekly_benefit(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "Tennessee CCAP maximum weekly benefit per child"
    definition_period = MONTH
    defined_for = "tn_ccap_eligible_child"
    reference = (
        "https://www.tn.gov/content/dam/tn/human-services/documents/Reimbursement_Rate_Chart_1.1.26.pdf",
        "https://www.tn.gov/content/dam/tn/human-services/documents/Current%20state%20rate%20and%20QRIS%20bonus%20table.pdf",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.tn.dhs.ccap.rates
        provider_type = person("tn_ccap_provider_type", period)
        county_tier = person.household("tn_ccap_county_tier", period)
        age_category = person("tn_ccap_age_category", period)
        qris_tier = person("tn_ccap_qris_tier", period)

        # Base weekly state rate by provider type, county tier, and age category.
        base_rate = select(
            [
                provider_type == TNCCAPProviderType.CHILD_CARE_CENTER,
                provider_type == TNCCAPProviderType.GROUP_HOME,
                provider_type == TNCCAPProviderType.FAMILY_HOME,
                provider_type == TNCCAPProviderType.AUTHORIZED,
            ],
            [
                p.child_care_center[county_tier][age_category],
                p.group_home[county_tier][age_category],
                p.family_home[county_tier][age_category],
                p.authorized[county_tier][age_category],
            ],
            default=p.child_care_center[county_tier][age_category],
        )

        # Age differential: infants and (through September 2025) toddlers.
        age_differential = select(
            [
                age_category == TNCCAPAgeCategory.INFANT,
                age_category == TNCCAPAgeCategory.TODDLER,
            ],
            [p.infant_differential, p.toddler_differential],
            default=0,
        )
        # Disability / special-needs differential.
        is_disabled = person("is_disabled", period.this_year)
        disability_differential = is_disabled * p.disability_differential

        is_licensed_provider = provider_type != TNCCAPProviderType.AUTHORIZED
        qris_rate = np.floor(base_rate * (1 + p.qris_bonus[qris_tier]) + 0.5)
        quality_adjusted_rate = where(
            is_licensed_provider,
            qris_rate,
            base_rate,
        )
        full_time_rate = (
            quality_adjusted_rate
            * (1 + age_differential)
            * (1 + disability_differential)
        )

        # Part-time care pays half the full-time rate, rounded up, but chart
        # footnote (a) restricts halving to Infant, Toddler, and Preschool;
        # school-age children in before/after-school care keep the full
        # School-In rate.
        is_part_time = person("tn_ccap_part_time", period)
        age_allows_halving = (
            (age_category == TNCCAPAgeCategory.INFANT)
            | (age_category == TNCCAPAgeCategory.TODDLER)
            | (age_category == TNCCAPAgeCategory.PRESCHOOL)
        )
        part_time_rate = np.ceil(full_time_rate * p.part_time_share)
        rate = where(is_part_time & age_allows_halving, part_time_rate, full_time_rate)

        # A child not in care draws no rate.
        hours = person("childcare_hours_per_week", period.this_year)
        return where(hours > 0, rate, 0)
