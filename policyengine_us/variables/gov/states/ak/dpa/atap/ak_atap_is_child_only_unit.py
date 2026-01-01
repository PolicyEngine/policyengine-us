from policyengine_us.model_api import *


class ak_atap_is_child_only_unit(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Alaska ATAP child-only assistance unit"
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/alaska/7-AAC-45.520"
    defined_for = StateCode.AK

    def formula(spm_unit, period, parameters):
        # Child-only unit has no caretaker relative receiving assistance
        # This is an approximation: unit has children but no adults
        person = spm_unit.members
        is_child = person("is_child", period.this_year)
        has_children = spm_unit.any(is_child)
        all_children = spm_unit.all(is_child)
        return has_children & all_children
