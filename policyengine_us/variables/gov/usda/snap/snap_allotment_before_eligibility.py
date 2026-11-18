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
    reference = (
        "https://www.law.cornell.edu/cfr/text/7/273.10#e_2_ii",
        "https://www.govinfo.gov/content/pkg/CFR-2017-title7-vol4/pdf/CFR-2017-title7-vol4-sec273-10.pdf#page=8",
        "https://www.govinfo.gov/content/pkg/FR-2017-01-06/pdf/2016-30663.pdf#page=30",
    )
    unit = USD

    def formula(spm_unit, period, parameters):
        expected_contribution = spm_unit("snap_expected_contribution", period)
        max_allotment = spm_unit("snap_max_allotment", period)
        min_allotment = spm_unit("snap_min_allotment", period)
        allotment = max_(min_allotment, max_allotment - expected_contribution)
        p = parameters(period).gov.usda.snap
        larger_unit = (
            spm_unit("snap_unit_size", period) > p.min_allotment.maximum_household_size
        )
        uplift = larger_unit & np.isin(allotment, p.low_allotment_uplift)
        return allotment + uplift
