from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.ne.dhhs.child_care_subsidy.ne_child_care_subsidy_provider_type import (
    NEChildCareSubsidyProviderType,
)
from policyengine_us.variables.gov.states.ne.dhhs.child_care_subsidy.ne_child_care_subsidy_age_group import (
    NEChildCareSubsidyAgeGroup,
)


class ne_child_care_subsidy_optional_fees(Variable):
    value_type = float
    entity = Person
    unit = USD
    definition_period = MONTH
    label = "Nebraska Child Care Subsidy approved optional fees"
    defined_for = "ne_child_care_subsidy_provider_eligible"
    reference = (
        "https://dhhs.ne.gov/Child%20Care%20Documents/Subsidy-Rates.pdf#page=1",
        "https://dhhs.ne.gov/Guidance%20Docs/Title%20392%20-%20Child%20Care%20Subsidy.pdf#page=9",
        "https://rules.nebraska.gov/api/fileStorage/GetAsByteArray/title-pdfs/Title_392.pdf/180#page=22",
        "https://rules.nebraska.gov/api/fileStorage/GetAsByteArray/title-pdfs/Title_392.pdf/180#page=23",
        "https://rules.nebraska.gov/api/fileStorage/GetAsByteArray/title-pdfs/Title_392.pdf/180#page=24",
        "https://rules.nebraska.gov/api/fileStorage/GetAsByteArray/title-pdfs/Title_392.pdf/180#page=25",
        "https://dhhs.ne.gov/Guidance%20Docs/Title%20392%20-%20Child%20Care%20Subsidy.pdf#page=10",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ne.dhhs.child_care_subsidy.fees
        provider = person("ne_child_care_subsidy_provider_type", period)
        licensed = (provider == NEChildCareSubsidyProviderType.CENTER) | (
            provider == NEChildCareSubsidyProviderType.HOME_I_II
        )
        transportation_occurrences = max_(
            person("ne_child_care_subsidy_transportation_occurrences", period),
            0,
        )
        spm_unit = person.spm_unit
        gross_income = spm_unit("ne_child_care_subsidy_gross_income", period)
        fpg = spm_unit("ne_child_care_subsidy_fpg", period)
        eligible_category = (
            spm_unit("is_tanf_enrolled", period)
            | (gross_income <= np.ceil(fpg))
            | spm_unit("ne_child_care_subsidy_categorical_waived", period)
        )
        transportation = (
            transportation_occurrences * p.transportation * licensed * eligible_category
        )
        summer_approved = person(
            "ne_child_care_subsidy_summer_activity_fee_approved", period
        )
        summer_month = np.isin(period.start.month, p.summer_activity.months)
        age_group = person("ne_child_care_subsidy_age_group", period)
        summer_age_eligible = age_group != NEChildCareSubsidyAgeGroup.INFANT
        summer = where(
            summer_approved & summer_month & summer_age_eligible & licensed,
            min_(
                p.summer_activity.monthly,
                p.summer_activity.annual_cap,
            ),
            0,
        )

        registration_amount = select(
            [
                provider == NEChildCareSubsidyProviderType.CENTER,
                provider == NEChildCareSubsidyProviderType.HOME_I_II,
                provider == NEChildCareSubsidyProviderType.LICENSE_EXEMPT_FAMILY_HOME,
                provider == NEChildCareSubsidyProviderType.LICENSE_EXEMPT_IN_HOME,
                provider == NEChildCareSubsidyProviderType.NONE,
            ],
            [
                p.registration.center,
                p.registration.home,
                0,
                0,
                0,
            ],
            default=0,
        )
        count_limit = where(
            person("ne_child_care_subsidy_new_provider", period),
            p.registration.new_provider_max_per_year,
            p.registration.continuing_provider_max_per_year,
        )
        paid_before_month = max_(
            person("ne_child_care_subsidy_registration_fees_paid_ytd", period),
            0,
        )
        remaining_count = max_(count_limit - paid_before_month, 0)
        approved_count = clip(
            person("ne_child_care_subsidy_registration_fee_count", period),
            0,
            remaining_count,
        )
        return transportation + summer + registration_amount * approved_count
