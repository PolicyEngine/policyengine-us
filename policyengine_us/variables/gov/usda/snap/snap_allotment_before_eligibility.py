from policyengine_us.model_api import *


class snap_allotment_before_eligibility(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = MONTH
    label = "SNAP allotment before eligibility screening"
    documentation = (
        "Calculated SNAP allotment, including the minimum for one- and two-person "
        "units, before eligibility screening. This allows zero-allotment "
        "participation rules to use the benefit calculation without a cycle."
    )
    reference = "https://www.law.cornell.edu/cfr/text/7/273.10#e_2_ii"
    unit = USD

    def formula(spm_unit, period, parameters):
        expected_contribution = spm_unit("snap_expected_contribution", period)
        max_allotment = spm_unit("snap_max_allotment", period)
        min_allotment = spm_unit("snap_min_allotment", period)
        return max_(min_allotment, max_allotment - expected_contribution)
