from policyengine_us.model_api import *


class dc_snap_temporary_local_benefit(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = MONTH
    documentation = "DC temporary SNAP benefit amount"
    label = "DC temporary local SNAP benefit amount"
    reference = "https://dhs.dc.gov/page/give-snap-raise-heres-what-expect"
    unit = USD
    defined_for = StateCode.DC

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.dc.snap

        max_allotments = parameters(period).gov.usda.snap.max_allotment

        snap_region = spm_unit.household("snap_region_str", period)
        household_size = spm_unit("spm_unit_size", period).astype(str)

        applicable_months = min_(MONTHS_IN_YEAR, p.max_months)

        dc_local_allotment = (
            max_allotments.main[snap_region][household_size]
            * p.rate
            * applicable_months
        )

        dc_monthly_local_allotment = dc_local_allotment / MONTHS_IN_YEAR

        return dc_monthly_local_allotment
