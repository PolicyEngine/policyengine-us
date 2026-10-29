from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.resources.deemed._ssi_spouses import (
    _ssi_couple_total,
    _ssi_spouse_index,
)


def state_couple_total(person, year, values):
    """Spouse totals for state rules that retain a declared marriage apart.

    A two-person marital unit declares the spouses even when they occupy
    different households. Larger default groups instead use SSI's identified
    spouse pair, so an unrelated adult cannot enter the spouse's budget.
    Callers apply their own medical-separation, entry-month or care conditions;
    this helper does not change federal SSI's co-residence test.
    """
    return where(
        person.marital_unit.nb_persons() == 2,
        person.marital_unit.sum(values),
        _ssi_couple_total(person, year, values),
    )


def state_is_married(person, year):
    """Declared spouses, including apart, or the identified default-group pair."""
    return (person.marital_unit.nb_persons() == 2) | (
        _ssi_spouse_index(person, year) >= 0
    )
