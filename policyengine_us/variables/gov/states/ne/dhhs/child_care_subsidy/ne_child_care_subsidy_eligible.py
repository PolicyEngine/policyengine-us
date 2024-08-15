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
        print("\ntestcase")
        p = parameters(period).gov.states.ne.dhhs.child_care_subsidy
        person = spm_unit.members
        eligible_parents = spm_unit.sum(
            spm_unit.members("ne_child_care_subsidy_eligible_parent", period)
        )
        has_eligible_parents = eligible_parents > 0
        print("has eligible parents", has_eligible_parents)
        eligible_children = spm_unit.sum(
            spm_unit.members("ne_child_care_subsidy_eligible_child", period)
        )
        has_eligible_children = eligible_children > 0
        print("has eligible children", has_eligible_children)
        income_eligible = spm_unit(
            "ne_child_care_subsidy_income_eligible", period
        )
        return has_eligible_parents & has_eligible_children & income_eligible
