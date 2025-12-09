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
        p = (
            parameters(period)
            .gov.states["or"]
            .odhs.tanf.income.child_support_disregard
        )
        child_support_received = add(
            spm_unit, period, ["child_support_received"]
        )
        person = spm_unit.members
        age = person("age", period.this_year)
        is_child = age < 18
        num_children = spm_unit.sum(is_child)
        max_disregard_by_children = num_children * p.per_child
        max_disregard = min_(max_disregard_by_children, p.max)
        return min_(child_support_received, max_disregard)
