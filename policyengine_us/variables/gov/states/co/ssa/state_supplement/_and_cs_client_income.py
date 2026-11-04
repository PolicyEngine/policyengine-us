from policyengine_us.model_api import *


def and_cs_client_income(person, period, parameters):
    """An AND-CS client's own monthly income and their use of the $20 disregard.

    9 CCR 2503-5 3.549(A). Returns the client's gross earned income, gross
    unearned income other than SSI, the part of the $20 unearned income
    disregard applied to that unearned income, and the part of it that
    3.549(A)(2)(f) applies to earned income.

    Gross income uses SSI's earned and unearned income sources. 3.520.786
    limits exempt income to the items it lists, and SSI's student earned
    income exclusion (20 CFR 416.1112(c)(3)) is not one of them, so it is
    not deducted.
    """
    p = parameters(period).gov.states.co.ssa.state_supplement.income.disregards
    earned = person("ssi_earned_income", period)
    # 3.520.79 counts in-kind support and maintenance as unearned income.
    ism = person("co_ssa_in_kind_support_and_maintenance", period)
    unearned = person("ssi_unearned_income", period) + ism
    ssi = person("ssi", period)
    # 3.549(A)(2)(c)(1): a married client's $20 disregard is split with the
    # spouse.
    married = person.marital_unit.nb_persons() == 2
    disregard = where(married, p.unearned / 2, p.unearned)
    # 3.549(A)(2)(c)(2): a client whose only unearned income is SSI gets no
    # unearned income disregard; min_ gives 0 when there is no other
    # unearned income.
    unearned_disregard = min_(disregard, unearned)
    # 3.549(A)(2)(f): the client's own share of the disregard (half of the
    # $20 when married, as in OAP's 3.533(A)(2)(f)) less gross unearned
    # income, SSI included, reduces earned income when positive. A client
    # whose only unearned income is SSI has no disregard to pass on.
    receives_ssi = (ssi > 0) | person("receives_ssi", period)
    ssi_only = receives_ssi & (unearned == 0)
    earned_disregard = where(ssi_only, 0, max_(0, disregard - unearned - ssi))
    return earned, unearned, unearned_disregard, earned_disregard
