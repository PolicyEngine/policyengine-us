from policyengine_us.model_api import *


class ok_tanf(Variable):
    value_type = float
    entity = SPMUnit
    label = "Oklahoma TANF"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/oklahoma/OAC-340-10-3-59"
    )
    defined_for = "ok_tanf_eligible"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ok.dhs.tanf

        payment_standard = spm_unit("ok_tanf_payment_standard", period)
        countable_income = spm_unit("ok_tanf_countable_income", period)

        # Per OAC 340:10-3-59: Benefit = Payment Standard - Countable Income
        benefit = max_(payment_standard - countable_income, 0)

        # Per OAC 340:10-3-59: Minimum benefit is $10; if less, no payment issues
        return where(benefit >= p.benefit.minimum_benefit, benefit, 0)
