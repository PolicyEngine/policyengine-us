from policyengine_us.model_api import *


class wa_tanf_countable_resources(Variable):
    value_type = float
    entity = SPMUnit
    label = "Countable resources for Washington TANF"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://app.leg.wa.gov/wac/default.aspx?cite=388-470-0045",
        "https://app.leg.wa.gov/wac/default.aspx?cite=388-470-0070",
    )
    defined_for = StateCode.WA

    def formula(spm_unit, period, parameters):
        cash_assets = spm_unit("spm_unit_cash_assets", period.this_year)
        vehicle_count = spm_unit.household("household_vehicles_owned", period.this_year)
        vehicle_value = spm_unit.household("household_vehicles_value", period.this_year)

        # Washington counts some non-home real property, but current CPS
        # inputs do not distinguish homestead from other property. To avoid
        # counting the excluded home as a TANF resource, only liquid assets
        # and countable vehicle value are modeled here until a non-homestead
        # property input exists.
        # Washington excludes one transportation vehicle. We only observe
        # total household vehicle value and count, so treat the countable
        # portion as the average value of any vehicles beyond the first.
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
