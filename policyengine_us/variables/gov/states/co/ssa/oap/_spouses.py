from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.resources.deemed._ssi_spouses import (
    _ssi_couple_total,
    _ssi_spouse_index,
)


def co_oap_couple_total(person, year, values):
    """OAP spouses' values, including declared spouses living apart.

    9 CCR 2503-5 3.534(B)-(C) does not require spouses to share a
    household. A two-person marital unit therefore retains both spouses;
    larger default groups use SSI's identified spouse pair instead.
    """
    return where(
        person.marital_unit.nb_persons() == 2,
        person.marital_unit.sum(values),
        _ssi_couple_total(person, year, values),
    )


def co_oap_is_married(person, year):
    """Marriage for OAP's shared $20 disregard (3.533(A)(2)(c))."""
    return (person.marital_unit.nb_persons() == 2) | (
        _ssi_spouse_index(person, year) >= 0
    )
