from policyengine_us.model_api import *


class wa_tanf_countable_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Washington TANF countable earned income"
    unit = USD
    definition_period = MONTH
    reference = "https://app.leg.wa.gov/wac/default.aspx?cite=388-450-0170"
    defined_for = StateCode.WA

    def formula(spm_unit, period, parameters):
        gross_earned = add(spm_unit, period, ["tanf_gross_earned_income"])
        p = parameters(
            period
        ).gov.states.wa.dshs.tanf.income.deductions.earned_income_disregard

        if p.in_effect:
            remainder = max_(gross_earned - p.amount, 0)
        else:
            remainder = gross_earned

        return remainder * (1 - p.rate)
