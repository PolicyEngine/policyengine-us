from policyengine_us.model_api import *


class mt_tanf_countable_resources(Variable):
    value_type = float
    entity = SPMUnit
    label = "Montana Temporary Assistance for Needy Families (TANF) countable resources"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://dphhs.mt.gov/assets/hcsd/tanfmanual/TANF4021May012021.pdf#page=1",
        "https://dphhs.mt.gov/assets/hcsd/tanfmanual/TANF403-1Jan012018.pdf#page=1",
        "https://www.law.cornell.edu/regulations/montana/Mont-Admin-r-37.78.401",
    )
    defined_for = StateCode.MT

    def formula(spm_unit, period, parameters):
        cash_assets = spm_unit("spm_unit_cash_assets", period.this_year)
        vehicle_count = spm_unit.household("household_vehicles_owned", period.this_year)
        vehicle_value = spm_unit.household("household_vehicles_value", period.this_year)

        # Montana counts some non-home real property, but current CPS inputs
        # do not distinguish the excluded home from other property. Keep the
        # model conservative until we have a non-homestead property input.
        # Montana excludes one vehicle with the highest equity value. We only
        # observe total vehicle value and count, so approximate the countable
        # portion as the average value of vehicles beyond the first.
        # NOTE: This overstates countable resources when vehicles differ in
        # value (e.g., $11k + $1k → $6k countable vs $1k correct). A
        # highest_vehicle_value input would allow the exact rule.
        average_vehicle_value = where(
            vehicle_count > 0,
            vehicle_value / vehicle_count,
            0,
        )
        countable_vehicle_value = average_vehicle_value * max_(vehicle_count - 1, 0)
        return cash_assets + countable_vehicle_value
