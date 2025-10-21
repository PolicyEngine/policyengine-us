from policyengine_us.model_api import *


class fl_tanf_gross_unearned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Florida TANF gross unearned income"
    unit = USD
    definition_period = MONTH
    reference = "Florida Administrative Code Rule 65A-4.209"
    documentation = "Total unearned income including child support (minus first $50), SSI, retirement income, and other unearned sources"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.fl.dcf.tanf.income_disregards

        # Child support with $50 disregard
        child_support = spm_unit("child_support_received", period)
        child_support_disregard = p.child_support
        countable_child_support = max_(
            child_support - child_support_disregard, 0
        )

        # Other unearned income sources
        ssi = spm_unit("ssi", period)
        pension = spm_unit("pension_income", period)
        unemployment = spm_unit("unemployment_compensation", period)

        return countable_child_support + ssi + pension + unemployment
