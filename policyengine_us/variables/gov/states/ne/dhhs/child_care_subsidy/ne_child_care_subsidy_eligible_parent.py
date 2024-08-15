from policyengine_us.model_api import *


class ne_child_care_subsidy_eligible_parent(Variable):
    value_type = bool
    entity = Person
    label = "Nebraska Child Care Subsidy program eligible parent"
    definition_period = YEAR
    reference = (
        "https://nebraskalegislature.gov/laws/statutes.php?statute=68-1206",
        "https://dhhs.ne.gov/Pages/Child-Care-Subsidy-Information-for-Parents.aspx",
    )
    defined_for = StateCode.NE

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ne.dhhs.child_care_subsidy
        is_parent = person("is_mother", period) | person("is_father", period)
        qualifying_criteria = add(person, period, p.categorical)
        is_criteria_eligible = np.any(qualifying_criteria)
        return is_parent & is_criteria_eligible
