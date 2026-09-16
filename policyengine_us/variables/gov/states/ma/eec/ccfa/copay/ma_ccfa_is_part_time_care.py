from policyengine_us.model_api import *


class ma_ccfa_is_part_time_care(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "Massachusetts CCFA child receives part-time care"
    defined_for = StateCode.MA
    reference = (
        "https://www.mass.gov/doc/eecs-financial-assistance-policy-guide-february-1-2022/download#page=76",
        "https://www.mass.gov/doc/fiscal-year-2025-child-care-financial-assistance-daily-reimbursement-rates/download#page=2",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ma.eec.ccfa.copay
        daily_hours = person("childcare_hours_per_day", period.this_year)
        short_day = (daily_hours > 0) & (daily_hours <= p.maximum_part_time_daily_hours)
        # Modeling assumption: before- and after-school schedules are treated
        # as part-time care; the sources define part-time by daily hours only.
        schedule = person("ma_ccfa_schedule_type", period)
        return short_day | (schedule != schedule.possible_values.FULL_DAY)
