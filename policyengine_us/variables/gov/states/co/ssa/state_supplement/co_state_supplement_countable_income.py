from policyengine_us.model_api import *


class co_state_supplement_countable_income(Variable):
    value_type = float
    entity = Person
    label = "Colorado State Supplement countable income other than SSI"
    unit = USD
    definition_period = MONTH
    # PDF pages 93-94
    reference = "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?fileName=9+CCR+2503-5&ruleVersionId=12428#page=93"

    def formula(person, period, parameters):
        # 9 CCR 2503-5 3.549(A) counts each AND-CS client's own income. Where
        # SSI's couple computation applies, ssi_countable_income instead gives
        # each spouse half of the couple's pooled countable income. Both
        # spouses then receive SSI, so 3.549(F) deems neither spouse's income
        # to the other, and the client's own income is counted as follows.
        couple_computation = person("ssi_couple_computation_applies", period)
        p = parameters(period).gov.ssa.ssi.income.exclusions
        earned = max_(
            person("ssi_earned_income", period)
            - person("ssi_blind_or_disabled_working_student_exclusion", period),
            0,
        )
        unearned = person("ssi_unearned_income", period) + person(
            "ssi_in_kind_support_and_maintenance", period
        )
        ssi = person("ssi", period)
        # 3.549(A)(2)(c): $20 is deducted from unearned income other than SSI,
        # split between married spouses; a client whose only unearned income
        # is SSI gets no unearned income disregard.
        unearned_disregard = min_(p.general / 2, unearned)
        # 3.549(A)(2)(f): only when the client's gross unearned income, SSI
        # included, is under $20 does the difference reduce earned income.
        earned_disregard = where(unearned > 0, max_(0, p.general - unearned - ssi), 0)
        # 3.549(A)(1): deduct $65 from gross earned income and halve the rest.
        countable_earned = max_(0, earned - p.earned - earned_disregard) * (
            1 - p.earned_share
        )
        own_countable = unearned - unearned_disregard + countable_earned
        return where(
            couple_computation,
            own_countable,
            person("ssi_countable_income", period),
        )
