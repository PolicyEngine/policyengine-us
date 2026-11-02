from policyengine_us.model_api import *


class fl_tca_200_and_half_disregard_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Florida TCA eligible for the $200 and 1/2 earned income disregard"
    definition_period = MONTH
    reference = (
        "https://www.leg.state.fl.us/statutes/index.cfm?App_mode=Display_Statute&URL=0400-0499/0414/Sections/0414.095.html",
        "https://www.leg.state.fl.us/statutes/index.cfm?App_mode=Display_Statute&URL=0400-0499/0414/Sections/0414.085.html",
        "https://www.flrules.org/gateway/ruleNo.asp?id=65A-4.209",
        "https://ffic.myflfamilies.com/manual/2400.pdf#page=27",
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

    Condition (2) is tested on the standard filing unit's income. The statute
    asks whether the individual is "eligible for participation in the program
    without the earnings disregard", and participation is a family test:
    414.085(1)(a) limits participation to "families whose gross family income"
    is at most 185 percent of the poverty level, and F.A.C. 65A-4.209(2) makes
    a unit financially eligible when "the total average gross monthly income
    less any applicable disregards of the standard filing unit" does not
    exceed the payment standard. The manual's own steps add "deemed and
    unearned income", and 65A-4.209(2)(b) counts deemed income in the
    assistance group's income, so the compared amount is the group's.
    Per 2420.0304 the $90 is budgeted "for each individual whose earned income
    is considered", so the test subtracts $90 from each earner's earnings.
    """

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.fl.dcf.tanf.income.disregard
        # 2420.0315(1): eligible for and received TCA in one of the past four
        # months (414.095(11)(a)1: a current participant in the program).
        current_participant = spm_unit("is_tanf_enrolled", period)
        person = spm_unit.members
        gross_earned = person("tanf_gross_earned_income", period)
        earned_after_standard = spm_unit.sum(
            max_(gross_earned - p.standard_disregard, 0)
        )
        unearned = add(spm_unit, period, ["tanf_gross_unearned_income"])
        payment_standard = spm_unit("fl_tca_payment_standard", period)
        # 2420.0315(2): the unit's gross countable income less the $90 standard
        # earned income disregard of each earner, compared to the payment
        # standard.
        income_after_standard = earned_after_standard + unearned
        return current_participant | (income_after_standard < payment_standard)
