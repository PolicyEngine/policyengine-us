from policyengine_us.model_api import *


class nm_works_child_support_deduction(Variable):
    value_type = float
    entity = SPMUnit
    label = "New Mexico Works child support deduction"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.srca.nm.gov/parts/title08/08.102.0520.html",
        "https://www.hca.nm.gov/2023/01/10/human-services-department-to-pass-through-more-money-to-low-income-families/",
    )
    defined_for = StateCode.NM

    def formula(spm_unit, period, parameters):
        # Per 8.102.520.9.J NMAC:
        # - $50 disregard on child support received
        # - Passthrough: $100 for 1 child, $200 for 2+ children (since Jan 2023)
        p = parameters(
            period
        ).gov.states.nm.hca.nm_works.income.deductions.child_support

        child_support_received = add(
            spm_unit, period, ["child_support_received"]
        )
        num_children = spm_unit("spm_unit_count_children", period.this_year)

        total_deduction = p.disregard + p.passthrough.calc(num_children)
        return min_(child_support_received, total_deduction)
