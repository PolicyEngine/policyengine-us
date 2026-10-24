from policyengine_us.model_api import *


class nm_ccap_activity_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for New Mexico CCAP based on activity requirements"
    definition_period = MONTH
    defined_for = StateCode.NM
    reference = (
        "https://www.srca.nm.gov/parts/title08/08.015.0002.html",
        "https://www.srca.nm.gov/parts/title08/08.009.0003.html",
        # PDF pages 3, 5, 10
        "https://prod-rf-lambda.rtssaas.com/PublicFiles/d89c47bd0d70402dba89b03a22bda6d1/b0e207a9-a1a3-412d-9660-0a6e925f6f25/8.9.3.pdf#page=3",
    )

    def formula(spm_unit, period, parameters):
        # 8.15.2.11.I / 8.15.2.7 (8.9.3.11.H / 8.9.3.7 from 2022-11-01):
        # benefits are for families working, attending school, or in a
        # job-training/educational program. The rule requires the activity to
        # be present (it does not set a minimum-hours floor), so we test for
        # any work hours or full-time student status. Each head/spouse
        # caretaker must independently meet the activity requirement.
        # From 2026-09-09, 8.9.3.10.H also lists part-time study, TANF
        # receipt, homelessness, foster parents, grandparents raising a
        # grandchild and other statuses, which are modeled here only through
        # meets_ccdf_activity_test.
        person = spm_unit.members
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period.this_year)
        hours_worked = person("weekly_hours_worked", period.this_year)
        is_student = person("is_full_time_student", period.this_year)
        individually_eligible = (hours_worked > 0) | is_student
        has_caretaker = spm_unit.sum(is_head_or_spouse) > 0
        no_ineligible_caretaker = (
            spm_unit.sum(is_head_or_spouse & ~individually_eligible) == 0
        )
        # Fallback for approved activities not modeled individually here -- job
        # training, job search, and temporary leave from work or school
        # (8.15.2.7, 8.9.3.7): set meets_ccdf_activity_test to flag the unit as
        # meeting the activity requirement.
        meets_ccdf = spm_unit("meets_ccdf_activity_test", period.this_year)
        return (has_caretaker & no_ineligible_caretaker) | meets_ccdf
