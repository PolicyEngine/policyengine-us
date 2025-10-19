from policyengine_us.model_api import *


class tx_tanf_child_support_deduction(Variable):
    value_type = float
    entity = SPMUnit
    label = "Texas TANF child support deduction"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.hhs.texas.gov/handbooks/texas-works-handbook/a-1420-types-deductions#a-1422-75-disregard-deduction",
        "https://www.law.cornell.edu/regulations/texas/1-Tex-Admin-Code-SS-372-404",
    )
    defined_for = StateCode.TX

    def formula(spm_unit, period, parameters):
        # Up to $75/month in child support can be deducted per household
        p = parameters(period).gov.states.tx.tanf.income
        child_support = spm_unit("child_support_received", period)

        return min_(child_support, p.deductions.child_support)
