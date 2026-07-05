from policyengine_us.model_api import *


class hi_cdcc_income_floor_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Hawaii income floor eligible"
    defined_for = StateCode.HI
    definition_period = YEAR
    reference = (
        "https://files.hawaii.gov/tax/legal/hrs/hrs_235.pdf#page=47",
        "https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=28",
        "https://files.hawaii.gov/tax/forms/2022/schx_i.pdf#page=2",
    )

    def formula(person, period, parameters):
        # HRS §235-55.6(d)(2) deems earned income only for a spouse who is a
        # student or incapable of caring for oneself, so the floor requires a
        # married couple and never applies to a single filer's own earnings.
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        married = person.tax_unit("tax_unit_married", period)
        student_or_incapable = person("is_full_time_student", period) | person(
            "is_incapable_of_self_care", period
        )
        return head_or_spouse & married & student_or_incapable
