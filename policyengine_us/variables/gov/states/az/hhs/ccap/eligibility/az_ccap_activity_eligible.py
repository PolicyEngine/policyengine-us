from policyengine_us.model_api import *


class az_ccap_activity_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Arizona Child Care Assistance Program based on activity"
    definition_period = MONTH
    defined_for = StateCode.AZ
    reference = (
        "https://des.az.gov/services/child-and-family/child-care/how-apply-for-child-care-assistance",
        "https://apps.azsos.gov/public_services/Title_06/6-05.pdf#page=25",
    )

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        head_or_spouse = person("is_tax_unit_head_or_spouse", period.this_year)
        working = person("weekly_hours_worked", period.this_year) > 0
        student = person("is_full_time_student", period.this_year)
        unable_to_care = person("is_disabled", period.this_year)
        eligible_person = working | student | unable_to_care
        return spm_unit.sum(head_or_spouse & ~eligible_person) == 0
