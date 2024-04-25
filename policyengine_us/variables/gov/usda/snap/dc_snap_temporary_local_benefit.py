from policyengine_us.model_api import *


class dc_snap_temporary_local_benefit(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = MONTH
    documentation = "DC temporary SNAP benefit amount"
    label = "DC temporary local SNAP benefit amount"
    reference = (
        "https://dhs.dc.gov/page/give-snap-raise-heres-what-expect",
        "https://code.dccouncil.gov/us/dc/council/laws/24-301",
    )
    unit = USD
    defined_for = StateCode.DC

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.usda.snap.temporary_local_benefit.dc

        max_allotments = spm_unit("snap_max_allotment", period)

        return max_allotments * p.rate
