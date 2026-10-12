from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.ne.dhhs.child_care_subsidy.rates.ne_child_care_subsidy_provider_type import (
    NEChildCareSubsidyProviderType,
)


class NEChildCareSubsidyRateUnit(Enum):
    PARTIAL_DAY = "Partial day"
    FULL_DAY = "Full day"
    FULL_PLUS_PARTIAL = "Full day plus partial day"
    HOUR = "Hour"
    NONE = "No authorized care unit reported"


class ne_child_care_subsidy_rate_unit(Variable):
    value_type = Enum
    entity = Person
    possible_values = NEChildCareSubsidyRateUnit
    default_value = NEChildCareSubsidyRateUnit.NONE
    definition_period = MONTH
    label = "Nebraska Child Care Subsidy authorized rate unit"
    defined_for = StateCode.NE
    reference = (
        "https://dhhs.ne.gov/Documents/CC-Subsidy-Provider-Booklet.pdf#page=31",
        "https://rules.nebraska.gov/api/fileStorage/GetAsByteArray/title-pdfs/Title_392.pdf/180#page=16",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ne.dhhs.child_care_subsidy
        provider = person("ne_child_care_subsidy_provider_type", period)
        hours = min_(
            person("childcare_hours_per_day", period.this_year),
            p.activity.max_daily_hours,
        )
        weekly_hours = person("ne_child_care_subsidy_authorized_weekly_hours", period)
        # Unreported daily hours default to a full-day authorization so
        # survey households without care schedule detail keep a priceable
        # unit under the rate matrix.
        derived = select(
            [
                (provider == NEChildCareSubsidyProviderType.LICENSE_EXEMPT_IN_HOME)
                & (weekly_hours > 0),
                hours <= 0,
                hours < p.provider.partial_day_max_hours,
                hours < p.provider.full_day_max_hours,
                hours <= p.activity.max_daily_hours,
            ],
            [
                NEChildCareSubsidyRateUnit.HOUR,
                NEChildCareSubsidyRateUnit.FULL_DAY,
                NEChildCareSubsidyRateUnit.PARTIAL_DAY,
                NEChildCareSubsidyRateUnit.FULL_DAY,
                NEChildCareSubsidyRateUnit.FULL_PLUS_PARTIAL,
            ],
            default=NEChildCareSubsidyRateUnit.NONE,
        )
        return derived
