from policyengine_us.model_api import *


class fl_tanf_categorically_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Florida TANF categorically eligible"
    definition_period = MONTH
    reference = (
        "Florida Statute § 414.095; Florida Administrative Code Rule 65A-4.208"
    )
    documentation = "Meets categorical eligibility: families with children under 18, pregnant women, or children under 19 in high school"

    def formula(spm_unit, period, parameters):
        # Check for children under 18
        person = spm_unit.members
        age = person("age", period)
        is_child = age < 18

        has_children = spm_unit.any(is_child)

        # Check for pregnant women
        is_pregnant = person("is_pregnant", period)
        has_pregnant_member = spm_unit.any(is_pregnant)

        return has_children | has_pregnant_member
