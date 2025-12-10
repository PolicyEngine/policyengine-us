from policyengine_us.model_api import *


class or_tanf_child_support_disregard(Variable):
    value_type = float
    entity = SPMUnit
    label = "Oregon TANF child support disregard"
    unit = USD
    definition_period = MONTH
    reference = "https://oregon.public.law/rules/oar_461-145-0080"
    defined_for = StateCode.OR

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states["or"].odhs.tanf
        child_support_received = add(
            spm_unit, period, ["child_support_received"]
        )
        person = spm_unit.members
        age = person("age", period.this_year)
        is_child = age < p.age_threshold.minor_child
        num_children = spm_unit.sum(is_child)
        disregard = p.income.child_support_disregard
        max_disregard_by_children = num_children * disregard.per_child
        max_disregard = min_(max_disregard_by_children, disregard.max)
        return min_(child_support_received, max_disregard)
