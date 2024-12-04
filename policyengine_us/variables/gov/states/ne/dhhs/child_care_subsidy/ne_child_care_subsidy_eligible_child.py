from policyengine_us.model_api import *


class ne_child_care_subsidy_eligible_child(Variable):
    value_type = bool
    entity = Person
    label = "Nebraska Child Care Subsidy program eligible child"
    definition_period = YEAR
    reference = (
        "https://nebraskalegislature.gov/laws/statutes.php?statute=68-1206",
        "https://dhhs.ne.gov/Pages/Child-Care-Subsidy-Information-for-Parents.aspx",
    )
    defined_for = StateCode.NE

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.states.ne.dhhs.child_care_subsidy.age_threshold
        age = person("age", period)
        has_special_needs = person("ne_dhhs_has_special_needs", period)
        age_threshold = where(has_special_needs, p.special_needs, p.base)
        return age <= age_threshold
