from policyengine_us.model_api import *
from policyengine_us.tools.childcare import childcare_hours_for_weekly_schedule


class WISharesTimeCategory(Enum):
    PART_TIME = "Part time"
    FULL_TIME = "Full time"


class wi_shares_time_category(Variable):
    value_type = Enum
    entity = Person
    possible_values = WISharesTimeCategory
    default_value = WISharesTimeCategory.FULL_TIME
    definition_period = MONTH
    label = "Wisconsin Shares authorization time category"
    defined_for = StateCode.WI
    reference = (
        "https://dcf.wisconsin.gov/wisconsin-shares/wisconsin-shares-handbook-july-2026#page=111",
        "https://dcf.wisconsin.gov/wisconsin-shares/wisconsin-shares-handbook-july-2026#page=155",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.wi.dcf.shares.hours
        # Authorizations of 20 weekly hours or less are part time;
        # authorizations of more than 20 weekly hours are full time
        # (Section 16.1.1).
        weekly_hours = childcare_hours_for_weekly_schedule(person, period)
        # Zero also represents unknown hours, so retain full-time pricing.
        return where(
            (weekly_hours == 0) | (weekly_hours > p.part_time_max_weekly_hours),
            WISharesTimeCategory.FULL_TIME,
            WISharesTimeCategory.PART_TIME,
        )
