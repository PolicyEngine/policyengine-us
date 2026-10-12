from policyengine_us.model_api import *


class fl_tca_200_and_half_disregard_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Florida TCA eligible for the $200 and 1/2 earned income disregard"
    definition_period = MONTH
    reference = "https://ffic.myflfamilies.com/manual/2400.pdf"
    defined_for = StateCode.FL
    documentation = """
    Whether the assistance group may receive the remainder of the "$200 and 1/2"
    earned income disregard under DCF ESS Program Policy Manual 2420.0314-.0315.

    Per 2420.0315, a member receives the $200 and 1/2 disregard if the individual:
      (1) has been eligible for and received TCA in one of the past four months; OR
      (2) has gross countable income (earned + unearned), less the $90 standard
          earned income disregard, that is less than the applicable payment
          standard.

    PolicyEngine cannot observe prior-month TCA receipt from a static snapshot, so
    condition (1) is not represented. This variable encodes the computable
    condition (2): (gross earned + unearned - $90 standard disregard) < payment
    standard. Because condition (1) can only expand eligibility, applying condition
    (2) alone is the conservative, manual-aligned choice for new applicants; it
    understates eligibility only for continuing recipients whose income has risen
    above the payment standard after the $90 disregard.
    """

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.fl.dcf.tanf.income.disregard
        gross_earned = add(spm_unit, period, ["tanf_gross_earned_income"])
        unearned = add(spm_unit, period, ["tanf_gross_unearned_income"])
        payment_standard = spm_unit("fl_tca_payment_standard", period)
        # 2420.0315(2): gross countable income less the $90 standard earned income
        # disregard, compared to the payment standard.
        income_after_standard = max_(gross_earned - p.standard_disregard, 0) + unearned
        return income_after_standard < payment_standard
