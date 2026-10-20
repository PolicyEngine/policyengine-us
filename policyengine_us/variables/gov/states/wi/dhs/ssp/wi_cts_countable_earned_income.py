from policyengine_us.model_api import *


class wi_cts_countable_earned_income(Variable):
    value_type = float
    entity = Person
    label = "Wisconsin CTS individual countable earned income"
    definition_period = MONTH
    unit = USD
    reference = "https://www.dhs.wisconsin.gov/publications/p23131-25-01.pdf#page=31"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.wi.dhs.ssp.cts
        earned = person("wi_cts_gross_earned_income", period)
        continuing_minor = (
            person("age", period.this_year) < p.minor_age_limit
        ) & person("wi_cts_received_recently", period)
        exempt = continuing_minor & (
            person("is_full_time_student", period.this_year)
            | (
                person("wi_cts_part_time_student", period)
                & (
                    person("weekly_hours_worked", period.this_year)
                    < p.student_hours_limit
                )
            )
        )
        flat = (
            continuing_minor
            | person("wi_cts_additional_flat_disregard", period)
            | person("wi_cts_additional_fraction_disregard", period)
        )
        fraction = continuing_minor | person(
            "wi_cts_additional_fraction_disregard", period
        )
        earned = max_(earned - p.work_expense - flat * p.earned_flat, 0) * (
            1 - fraction * p.earned_fraction
        )
        return where(exempt, 0, earned)
