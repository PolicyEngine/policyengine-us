from policyengine_us.model_api import *


class mn_tanf_countable_unearned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Minnesota MFIP countable unearned income"
    unit = USD
    definition_period = MONTH
    reference = "https://www.revisor.mn.gov/statutes/cite/142G/pdf"
    defined_for = StateCode.MN

    def formula(spm_unit, period, parameters):
        gross_unearned = spm_unit("tanf_gross_unearned_income", period)
        child_support = add(spm_unit, period, ["child_support_received"])
        child_support_disregard = spm_unit(
            "mn_tanf_child_support_disregard", period
        )

        countable_child_support = max_(
            child_support - child_support_disregard, 0
        )
        return gross_unearned - child_support + countable_child_support
