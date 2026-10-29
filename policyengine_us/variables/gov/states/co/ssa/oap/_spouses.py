from policyengine_us.variables.gov.states._spouses import (
    state_couple_total,
    state_is_married,
)


def co_oap_couple_total(person, year, values):
    """OAP spouses' values, including declared spouses living apart.

    9 CCR 2503-5 3.534(B)-(C) does not require spouses to share a
    household. A two-person marital unit therefore retains both spouses;
    larger default groups use SSI's identified spouse pair instead.
    """
    return state_couple_total(person, year, values)


def co_oap_is_married(person, year):
    """Marriage for OAP's shared $20 disregard (3.533(A)(2)(c))."""
    return state_is_married(person, year)
