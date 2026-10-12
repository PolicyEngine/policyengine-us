from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.income._apply_ssi_exclusions import (
    _apply_ssi_exclusions,
)


class co_state_supplement_countable_income(Variable):
    value_type = float
    entity = Person
    label = "Colorado State Supplement countable income"
    unit = USD
    definition_period = YEAR
    # PDF pages 93-94
    reference = "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?fileName=9+CCR+2503-5&ruleVersionId=12428#page=93"

    def formula(person, period, parameters):
        # 9 CCR 2503-5 3.549(A) counts each AND-CS client's own income. Where
        # SSI's couple computation applies, ssi_countable_income instead gives
        # each spouse half of the couple's pooled countable income. Both
        # spouses then receive SSI, so 3.549(F) deems neither spouse's income
        # to the other, and 3.549(A)(2)(c)(1) splits the $20 unearned income
        # disregard "between the client and the spouse"; it is split equally
        # here. Any part a spouse cannot use against unearned income goes to
        # their earned income (3.549(A)(2)(f)), as _apply_ssi_exclusions does.
        couple_computation = person("ssi_couple_computation_applies", period)
        earned = max_(
            person("ssi_earned_income", period)
            - person("ssi_blind_or_disabled_working_student_exclusion", period),
            0,
        )
        unearned = person("ssi_unearned_income", period) + person(
            "ssi_in_kind_support_and_maintenance", period
        )
        p = parameters(period).gov.ssa.ssi.income.exclusions
        own_countable = _apply_ssi_exclusions(
            earned,
            unearned,
            parameters,
            period,
            general_exclusion=p.general / 2,
        )
        return where(
            couple_computation,
            own_countable,
            person("ssi_countable_income", period),
        )
