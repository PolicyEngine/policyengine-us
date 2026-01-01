from policyengine_us.model_api import *


class ak_atap_is_pregnant_woman_only(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Alaska ATAP pregnant woman only unit"
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/alaska/7-AAC-45.520"
    defined_for = StateCode.AK

    def formula(spm_unit, period, parameters):
        # Pregnant woman with no other eligible children
        person = spm_unit.members
        is_pregnant = person("is_pregnant", period.this_year)
        is_child = person("is_child", period.this_year)

        has_pregnant_woman = spm_unit.any(is_pregnant)
        has_children = spm_unit.any(is_child)

        return has_pregnant_woman & ~has_children
