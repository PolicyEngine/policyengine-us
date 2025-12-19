from policyengine_us.model_api import *


class or_tanf_adjusted_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Oregon TANF adjusted income"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://oregon.public.law/rules/oar_461-001-0000",
        "https://oregon.public.law/rules/oar_461-160-0160",
    )
    defined_for = StateCode.OR

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states["or"].odhs.tanf.income
        countable_income = spm_unit("or_tanf_countable_income", period)
        gross_earned = add(spm_unit, period, ["tanf_gross_earned_income"])
        earned_income_disregard = gross_earned * p.earned_income_disregard_rate
        return max_(countable_income - earned_income_disregard, 0)
