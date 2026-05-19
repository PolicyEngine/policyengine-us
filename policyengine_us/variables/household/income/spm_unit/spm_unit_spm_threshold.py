from policyengine_us.model_api import *


class spm_unit_spm_threshold(Variable):
    value_type = float
    entity = SPMUnit
    label = "SPM unit's SPM poverty threshold"
    definition_period = YEAR
    unit = USD

    def formula_2015(spm_unit, period, parameters):
        """Rebuild the SPM threshold from current composition, current
        tenure, and the unit-specific geographic adjustment.

        Base reference thresholds and the Betson three-parameter
        equivalence scale come from ``spm-calculator``.
        """
        unadjusted_threshold = spm_unit(
            "spm_unit_unadjusted_spm_threshold",
            period,
        )
        geoadj = spm_unit("spm_unit_geographic_adjustment", period)
        return unadjusted_threshold * geoadj
