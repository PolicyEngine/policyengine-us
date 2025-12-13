from policyengine_us.model_api import *


class mn_mfip_child_support_disregard(Variable):
    value_type = float
    entity = SPMUnit
    label = "Minnesota MFIP child support disregard"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.revisor.mn.gov/statutes/cite/256P.06#stat.256P.06.3"
    )
    defined_for = StateCode.MN

    def formula(spm_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.mn.dcyf.mfip.income.child_support_disregard
        children = spm_unit("spm_unit_count_children", period.this_year)
        return p.amount.calc(children)
