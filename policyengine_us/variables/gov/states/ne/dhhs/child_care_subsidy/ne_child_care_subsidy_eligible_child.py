from policyengine_us.model_api import *


class ne_child_care_subsidy_eligible_child(Variable):
    value_type = bool
    entity = Person
    label = "Nebraska Child Care Subsidy program eligible child"
    definition_period = MONTH
    reference = (
        "https://rules.nebraska.gov/api/fileStorage/GetAsByteArray/title-pdfs/Title_392.pdf/180#page=9",
        "https://rules.nebraska.gov/api/fileStorage/GetAsByteArray/title-pdfs/Title_392.pdf/180#page=11",
    )
    defined_for = StateCode.NE

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ne.dhhs.child_care_subsidy.age_threshold
        age = person("age", period.this_year)
        has_special_needs = person("ne_dhhs_has_special_needs", period.this_year)
        enrolled = person.spm_unit("ne_child_care_subsidy_enrolled", period)
        age_eligible = (
            (age < p.base + 1)
            | (enrolled & (age < p.enrolled + 1))
            | (has_special_needs & (age < p.special_needs + 1))
        )
        immigration_eligible = person(
            "is_ccdf_immigration_eligible_child", period.this_year
        )
        return age_eligible & immigration_eligible
