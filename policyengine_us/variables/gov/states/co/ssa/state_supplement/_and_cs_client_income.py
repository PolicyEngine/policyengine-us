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
    # A joint couple's in-kind support and maintenance is one presumed
    # maximum value for the couple (ssi_pmv_amount), which SSI splits
    # equally between the spouses. 3.520.71(E) and 3.520.79(B)(6) charge an
    # SSI recipient the same ISM that SSA charges.
    ism = person("ssi_in_kind_support_and_maintenance", period)
    couple_computation = person("ssi_couple_computation_applies", period)
    ism = where(couple_computation, ism / 2, ism)
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
    # 3.549(A)(2)(f): only when the client's gross unearned income, SSI
    # included, is under $20 does the difference reduce earned income.
    earned_disregard = where(unearned > 0, max_(0, p.unearned - unearned - ssi), 0)
    return earned, unearned, unearned_disregard, earned_disregard
