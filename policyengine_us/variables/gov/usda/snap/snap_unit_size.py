from policyengine_us.model_api import *


class snap_unit_size(Variable):
    value_type = int
    entity = SPMUnit
    label = "SNAP unit size"
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/uscode/text/7/2014#b",
        "https://www.law.cornell.edu/uscode/text/7/2015#f",
    )

    def formula(spm_unit, period, parameters):
        unit_size = spm_unit("spm_unit_size", period.this_year)
        excluded_count = add(spm_unit, period, ["is_snap_excluded_member"])
        return max_(unit_size - excluded_count, 0)
