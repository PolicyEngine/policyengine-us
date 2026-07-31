from policyengine_us.model_api import *


class ne_child_care_subsidy_gross_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    definition_period = YEAR
    label = "Nebraska Child Care Subsidy gross earned income"
    defined_for = StateCode.NE
    reference = (
        "https://dhhs.ne.gov/Guidance%20Docs/Title%20392%20-%20Child%20Care%20Subsidy.pdf#page=3",
        "https://dhhs.ne.gov/Guidance%20Docs/Title%20392%20-%20Child%20Care%20Subsidy.pdf#page=4",
        "https://rules.nebraska.gov/api/fileStorage/GetAsByteArray/title-pdfs/Title_392.pdf/180#page=11",
        "https://rules.nebraska.gov/api/fileStorage/GetAsByteArray/title-pdfs/Title_392.pdf/180#page=13",
        "https://rules.nebraska.gov/api/fileStorage/GetAsByteArray/title-pdfs/Title_392.pdf/180#page=14",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ne.dhhs.child_care_subsidy.income
        person = spm_unit.members
        earned = add(person, period, p.sources.earned)
        age = person("age", period)
        in_school = (
            person("is_full_time_student", period)
            | person("is_part_time_college_student", period)
            | person("technical_institution_student", period)
        )
        excluded_student = in_school & (age < p.student_earner_age_threshold + 1)
        # Net self-employment inputs approximate statutory gross receipts less
        # allowable expenses; military income cannot isolate excluded combat pay.
        return spm_unit.sum(earned * ~excluded_student)
