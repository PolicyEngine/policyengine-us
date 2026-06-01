from policyengine_us.model_api import *


class az_ccap_activity_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Arizona Child Care Assistance Program based on activity"
    definition_period = MONTH
    defined_for = StateCode.AZ
    reference = (
        "https://des.az.gov/services/child-and-family/child-care/how-apply-for-child-care-assistance",
        "https://apps.azsos.gov/public_services/Title_06/6-05.pdf#page=26",
    )

    def formula(spm_unit, period, parameters):
        # R6-5-4912 qualifying activities: employment, education/training (with a
        # work requirement for adults), teen-parent education, inability to provide
        # care, drug/alcohol rehabilitation, court-ordered community service, and a
        # shelter case plan. We model employment and inability to provide care
        # (is_disabled); we don't separately track rehabilitation, court-ordered
        # community service, or shelter case plans at the moment.
        person = spm_unit.members
        head_or_spouse = person("is_tax_unit_head_or_spouse", period.this_year)
        # R6-5-4912(A)(1): employment, full or part-time, is a qualifying activity.
        working = person("weekly_hours_worked", period.this_year) > 0
        # R6-5-4912(A)(3) requires adults using education as their activity to also
        # work an average of >=20 hours/week (already captured by `working`), so
        # education on its own only qualifies teen parents under age 20 (A)(4).
        age = person("age", period.this_year)
        teen_parent_student = (age < 20) & person(
            "is_full_time_student", period.this_year
        )
        unable_to_care = person("is_disabled", period.this_year)
        eligible_person = working | teen_parent_student | unable_to_care
        return spm_unit.sum(head_or_spouse & ~eligible_person) == 0
