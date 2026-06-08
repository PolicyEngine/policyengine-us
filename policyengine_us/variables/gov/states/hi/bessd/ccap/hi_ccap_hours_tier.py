from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.hi.bessd.ccap.hi_ccap_provider_category import (
    HICCAPProviderCategory,
)


class HICCAPHoursTier(Enum):
    FULL_TIME = "Full-time"
    TWO_THIRDS = "Two-thirds"
    ONE_THIRD = "One-third"
    CASUAL = "Casual"


class hi_ccap_hours_tier(Variable):
    value_type = Enum
    entity = Person
    possible_values = HICCAPHoursTier
    default_value = HICCAPHoursTier.FULL_TIME
    definition_period = MONTH
    label = "Hawaii CCAP hours tier"
    defined_for = StateCode.HI
    reference = "https://humanservices.hawaii.gov/wp-content/uploads/2018/04/Child-Care-Rate-Table-2017-08-01.pdf"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.hi.bessd.ccap.hours_tier
        # Exhibit I bands are in monthly hours of care. Use the effective
        # authorized hours = lesser of the child's care hours and the
        # caretaker's activity hours (HAR 17-798.2-14(b)(1)).
        monthly_hours = person("hi_ccap_monthly_care_hours", period)
        # Before/after-school rows use a separate, lower-hour band scheme.
        provider_category = person("hi_ccap_provider_category", period)
        is_before_after = (
            provider_category == HICCAPProviderCategory.LICENSED_BEFORE_AFTER_SCHOOL
        ) | (provider_category == HICCAPProviderCategory.EXEMPT_BEFORE_AFTER_SCHOOL)
        # The bracket parameters return the integer index of the hours tier
        # enum (0=FULL_TIME, 1=TWO_THIRDS, 2=ONE_THIRD, 3=CASUAL).
        return where(
            is_before_after,
            p.before_after.calc(monthly_hours),
            p.standard.calc(monthly_hours),
        )
