from policyengine_us.model_api import *


class ak_atap_earned_income_deduction(Variable):
    value_type = float
    entity = SPMUnit
    label = "Alaska ATAP earned income deduction"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/alaska/7-AAC-45.480",
        "http://dpaweb.hss.state.ak.us/manuals/ta/700/760/760-2_work_incentive_deductions.htm",
    )
    defined_for = StateCode.AK

    def formula(spm_unit, period, parameters):
        # NOTE: This uses Tier 1 deduction (months 1-12) which is the most
        # favorable. PolicyEngine cannot track tier progression across months.
        # Actual tiers: 33%/25%/20%/15%/10%/0% based on months receiving ATAP.
        p = parameters(period).gov.states.ak.dpa.atap.income.deductions
        gross_earned = add(spm_unit, period, ["tanf_gross_earned_income"])

        # Step 1: Apply flat deduction
        flat_deduction = p.work_incentive_flat
        after_flat = max_(gross_earned - flat_deduction, 0)

        # Step 2: Apply percentage disregard to remainder
        percent_disregard = after_flat * p.work_incentive_percent

        return flat_deduction + percent_disregard
