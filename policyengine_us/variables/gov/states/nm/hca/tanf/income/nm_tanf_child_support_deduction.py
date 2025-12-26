from policyengine_us.model_api import *


class nm_tanf_child_support_deduction(Variable):
    value_type = float
    entity = SPMUnit
    label = "New Mexico TANF child support deduction"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.srca.nm.gov/parts/title08/08.102.0520.html",
        "https://www.hca.nm.gov/2023/01/10/human-services-department-to-pass-through-more-money-to-low-income-families/",
    )
    defined_for = StateCode.NM

    def formula(spm_unit, period, parameters):
        # Per 8.102.520.10 NMAC:
        # - $50 disregard on child support received
        # - Passthrough: $100 for 1 child, $200 for 2+ children
        p = parameters(period).gov.states.nm.hca.tanf.income.deductions

        child_support_received = add(
            spm_unit, period, ["child_support_received"]
        )

        # Count children in benefit group
        person = spm_unit.members
        age = person("age", period.this_year)
        age_threshold = parameters(period).gov.states.nm.hca.tanf.age_threshold
        is_child = age < age_threshold.minor_child
        num_children = spm_unit.sum(is_child)

        # Calculate disregard and passthrough
        disregard = p.child_support.disregard
        passthrough = p.child_support.passthrough.calc(num_children)
        total_deduction = disregard + passthrough

        return min_(child_support_received, total_deduction)
