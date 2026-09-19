from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.tx.twc.ccs.payment.tx_ccs_care_schedule import (
    TXCCSCareSchedule,
)


class tx_ccs_payment_care_schedule(Variable):
    value_type = Enum
    possible_values = TXCCSCareSchedule
    default_value = TXCCSCareSchedule.FULL_TIME
    entity = Person
    definition_period = MONTH
    label = "Texas Child Care Services (CCS) care schedule used for payment"
    defined_for = StateCode.TX
    reference = "https://www.twc.texas.gov/sites/default/files/ogc/docs/fr-809-ch-rev-12-12-twc.pdf#page=74"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.tx.twc.ccs.payment
        schedule = person("tx_ccs_care_schedule", period)
        daily_hours = person("childcare_hours_per_day", period.this_year)
        weekly_hours = person("childcare_hours_per_week", period.this_year)
        weekly_days = person("childcare_days_per_week", period.this_year)
        # Only convert weekly hours when the number of days is known. Prefer
        # reported daily hours if both daily and weekly inputs are supplied.
        hours = where(
            daily_hours > 0,
            daily_hours,
            np.divide(
                weekly_hours,
                weekly_days,
                out=np.zeros_like(weekly_hours),
                where=weekly_days > 0,
            ),
        )
        # Zero and omitted hours are indistinguishable. Use the full-day rate
        # as a modeling fallback; payment still requires billable care days.
        # Explicit authorization takes precedence over occasional attendance
        # differences (40 TAC 809.93(g) in the cited 2013 rules).
        return select(
            [
                schedule != TXCCSCareSchedule.UNSPECIFIED,
                (hours > 0) & (hours < p.full_time_min_hours),
            ],
            [schedule, TXCCSCareSchedule.PART_TIME],
            default=TXCCSCareSchedule.FULL_TIME,
        )
