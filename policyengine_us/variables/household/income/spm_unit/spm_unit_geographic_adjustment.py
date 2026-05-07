import numpy as np

from policyengine_us.model_api import *
from policyengine_us.variables.household.income.spm_unit.spm_unit_spm_threshold import (
    _reference_threshold_array,
)
from spm_calculator.equivalence_scale import spm_equivalence_scale


class spm_unit_geographic_adjustment(Variable):
    value_type = float
    entity = SPMUnit
    label = "SPM unit geographic adjustment"
    documentation = "Geographic adjustment applied to the SPM reference threshold."
    definition_period = YEAR
    default_value = 1.0

    def formula_2016(spm_unit, period, parameters):
        """Infer the location adjustment from prior-year threshold inputs.

        Datasets can provide this directly. For older datasets that only
        contain stored SPM thresholds, this preserves the implied adjustment.
        """
        prior_period = period.last_year
        cpi_u = parameters.gov.bls.cpi.cpi_u

        prior_threshold = spm_unit("spm_unit_spm_threshold", prior_period)
        prior_adults = spm_unit("spm_unit_count_adults", prior_period)
        prior_children = spm_unit("spm_unit_count_children", prior_period)
        prior_tenure = spm_unit("spm_unit_tenure_type", prior_period)

        prior_base = _reference_threshold_array(
            prior_tenure,
            prior_period.start.year,
            cpi_u,
        )
        prior_equiv_scale = spm_equivalence_scale(
            prior_adults,
            prior_children,
        )
        denominator = prior_base * prior_equiv_scale
        return np.divide(
            prior_threshold,
            denominator,
            out=np.ones_like(prior_threshold, dtype=float),
            where=(prior_threshold > 0) & (denominator > 0),
        )
