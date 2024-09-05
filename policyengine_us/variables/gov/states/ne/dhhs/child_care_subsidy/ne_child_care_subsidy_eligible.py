from policyengine_us.model_api import *


class ne_child_care_subsidy_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for the Nebraska Child Care Subsidy program"
    definition_period = YEAR
    reference = (
        "https://nebraskalegislature.gov/laws/statutes.php?statute=68-1206",
        "https://dhhs.ne.gov/Pages/Child-Care-Subsidy-Information-for-Parents.aspx",
    )
    defined_for = StateCode.NE

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ne.dhhs.child_care_subsidy
        person = spm_unit.members
        eligible_parent = person(
            "ne_child_care_subsidy_eligible_parent", period
        )
        eligible_parent_present = spm_unit.any(eligible_parent)
        eligible_child = person("ne_child_care_subsidy_eligible_child", period)
        eligible_child_present = spm_unit.any(eligible_child)
        income_eligible = spm_unit(
            "ne_child_care_subsidy_income_eligible", period
        )
        return (
            eligible_parent_present & eligible_child_present & income_eligible
        )
