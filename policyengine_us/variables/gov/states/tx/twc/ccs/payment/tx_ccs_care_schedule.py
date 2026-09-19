from policyengine_us.model_api import *


class TXCCSCareSchedule(Enum):
    FULL_TIME = "Full Time"
    PART_TIME = "Part Time"
    BLENDED = "Blended"


class tx_ccs_care_schedule(Variable):
    value_type = Enum
    possible_values = TXCCSCareSchedule
    default_value = TXCCSCareSchedule.FULL_TIME
    entity = Person
    definition_period = MONTH
    label = "Texas Child Care Services (CCS) care schedule"
    defined_for = StateCode.TX
    reference = (
        "https://www.twc.texas.gov/sites/default/files/ccel/docs/bcy25-board-max-provider-payment-rates-4-age-groups-twc.pdf",
        "https://www.twc.texas.gov/sites/default/files/ogc/docs/fr-809-ch-rev-12-12-twc.pdf#page=74",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.tx.twc.ccs.payment
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
        # Zero and omitted hours are indistinguishable. Retain the full-day
        # modeling fallback; payment still requires billable care days.
        # Explicit schedule inputs override this formula through core.
        is_part_time = (hours > 0) & (hours < p.full_time_min_hours)
        return where(
            is_part_time,
            TXCCSCareSchedule.PART_TIME,
            TXCCSCareSchedule.FULL_TIME,
        )
