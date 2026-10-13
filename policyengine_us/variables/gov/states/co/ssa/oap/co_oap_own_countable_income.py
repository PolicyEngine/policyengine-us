from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.co.ssa.oap._precision import (
    cents,
    ssi_paid,
)


class co_oap_own_countable_income(Variable):
    value_type = float
    entity = Person
    label = "Colorado Old Age Pension countable income of the client other than SSI"
    unit = USD
    definition_period = MONTH
    # Not restricted to Colorado: a client's spouse may live elsewhere
    # (3.534(C)). co_oap itself is defined only for Colorado residents.
    # PDF pages 68-73, 76-77
    reference = "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?fileName=9+CCR+2503-5&ruleVersionId=12428#page=68"

    def formula(person, period, parameters):
        # 9 CCR 2503-5 3.533(A) counts the client's own income whether or not
        # they are eligible for SSI. The SSI that 3.533(A)(2)(d) adds back is
        # added in co_oap.
        p = parameters(period).gov.states.co.ssa.oap.income
        # 3.520.786 limits exempt earned income to the items it lists, so
        # SSI's student earned income exclusion is not deducted.
        # Monthly amounts in cents, SSI as SSA pays it (see _precision.py).
        earned = cents(person("ssi_earned_income", period))
        ssi = ssi_paid(person("ssi", period))
        receives_ssi = ssi > 0
        unearned = person("co_oap_unearned_income", period) + person(
            "co_oap_in_kind_support_and_maintenance", period
        )
        # 3.533(A)(2)(c)(1): a married client's $20 disregard is split equally
        # with the spouse, so that no more than $20 applies to the couple.
        married = person.marital_unit.nb_persons() == 2
        disregard = where(married, p.disregards.unearned / 2, p.disregards.unearned)
        # 3.533(A)(2)(c): the disregard applies to unearned income other than
        # SSI; min_ gives 0 to a client whose only unearned income is SSI
        # (3.533(A)(2)(c)(2)).
        unearned_disregard = min_(disregard, unearned)
        # 3.533(A)(2)(f): when gross unearned income, SSI included, is under
        # $20, the rest of the disregard reduces earned income. A client whose
        # only unearned income is SSI has no disregard to pass on.
        ssi_only = receives_ssi & (unearned == 0)
        earned_disregard = where(ssi_only, 0, max_(0, disregard - unearned - ssi))
        # 3.533(A)(1): deduct $65 from gross earned income and halve the rest.
        countable_earned = (
            max_(0, earned - p.disregards.earned - earned_disregard)
            * p.disregards.earned_share
        )
        return unearned - unearned_disregard + countable_earned
