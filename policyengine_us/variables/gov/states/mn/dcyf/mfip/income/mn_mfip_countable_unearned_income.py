from policyengine_us.model_api import *


class mn_mfip_countable_unearned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Minnesota MFIP countable unearned income"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.revisor.mn.gov/statutes/cite/256P.06#stat.256P.06.3"
    )
    defined_for = StateCode.MN

    def formula(spm_unit, period, parameters):
        gross_unearned = add(spm_unit, period, ["tanf_gross_unearned_income"])
        child_support = add(spm_unit, period, ["child_support_received"])
        disregard = spm_unit("mn_mfip_child_support_disregard", period)
        countable_child_support = max_(child_support - disregard, 0)
        return gross_unearned - child_support + countable_child_support
