from policyengine_us.model_api import *


class fl_tca_200_and_half_disregard_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Florida TCA eligible for the $200 and 1/2 earned income disregard"
    definition_period = MONTH
    reference = (
        "https://www.leg.state.fl.us/statutes/index.cfm?App_mode=Display_Statute&URL=0400-0499/0414/Sections/0414.095.html",
        "https://ffic.myflfamilies.com/manual/2400.pdf#page=28",
    )
    defined_for = StateCode.FL
    documentation = """
    Whether the assistance group may receive the remainder of the "$200 and 1/2"
    earned income disregard under Florida Statutes 414.095(11)(a) and DCF ESS
    Program Policy Manual 2420.0314-.0315.

    Per 2420.0315, a member receives the $200 and 1/2 disregard if the individual:
      (1) has been eligible for and received TCA in one of the past four months; OR
      (2) has gross countable income (earned + unearned), less the $90 standard
          earned income disregard, that is less than the applicable payment
          standard.
    Florida Statutes 414.095(11)(a) requires the individual to be a current
    participant in the program, or eligible for participation without the
    earnings disregard. The statute does not mention the $90 standard
    disregard; the manual supplies the $90 and the test of income after it in
    condition (2).

    Condition (1) uses is_tanf_enrolled, which defaults to reported TANF
    receipt, to stand for receipt of TCA in one of the past four months.
    Condition (2) compares (gross earned + unearned - $90 standard disregard) to
    the payment standard.
    """

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.fl.dcf.tanf.income.disregard
        # 2420.0315(1): eligible for and received TCA in one of the past four
        # months (414.095(11)(a)1: a current participant in the program).
        current_participant = spm_unit("is_tanf_enrolled", period)
        gross_earned = add(spm_unit, period, ["tanf_gross_earned_income"])
        unearned = add(spm_unit, period, ["tanf_gross_unearned_income"])
        payment_standard = spm_unit("fl_tca_payment_standard", period)
        # 2420.0315(2): gross countable income less the $90 standard earned income
        # disregard, compared to the payment standard.
        income_after_standard = max_(gross_earned - p.standard_disregard, 0) + unearned
        return current_participant | (income_after_standard < payment_standard)
