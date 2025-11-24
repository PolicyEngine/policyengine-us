from policyengine_us.model_api import *


class mn_tanf_child_support_disregard(Variable):
    value_type = float
    entity = SPMUnit
    label = "Minnesota MFIP child support disregard"
    unit = USD
    definition_period = MONTH
    reference = "https://www.revisor.mn.gov/statutes/cite/142G/pdf"
    defined_for = StateCode.MN

    def formula(spm_unit, period, parameters):
        num_children = spm_unit("mn_tanf_count_children", period.this_year)
        p = parameters(
            period
        ).gov.states.mn.dhs.tanf.income.child_support_disregard

        return where(
            num_children >= 2,
            p.two_plus_children,
            where(num_children == 1, p.one_child, 0),
        )
