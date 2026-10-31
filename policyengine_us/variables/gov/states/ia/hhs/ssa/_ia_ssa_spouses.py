from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.resources.deemed._ssi_spouses import (
    _ssi_spouse_index,
)


def ia_ssa_spouse_value(person, period, values):
    """The co-resident spouse's value, excluding unrelated household adults."""
    spouse = _ssi_spouse_index(person, period.this_year)
    return where(spouse >= 0, values[np.maximum(spouse, 0)], np.zeros_like(values))
