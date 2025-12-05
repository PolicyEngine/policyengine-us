from policyengine_us.model_api import *


class in_tanf_countable_resources(Variable):
    value_type = float
    entity = SPMUnit
    label = "Indiana TANF countable resources"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.IN
    reference = (
        "https://iar.iga.in.gov/code/2026/470/10.3#470-10.3-4-2",
        "https://iga.in.gov/laws/2025/ic/titles/12/#12-14-2-1",
    )

    def formula(spm_unit, period, parameters):
        p = (
            parameters(period)
            .gov.states["in"]
            .fssa.tanf.resources.vehicle_exemption
        )
        total_assets = spm_unit("spm_unit_assets", period.this_year)
        vehicle_value = spm_unit.household(
            "household_vehicles_value", period.this_year
        )
        excluded_vehicle = min_(vehicle_value, p.amount)
        return max_(total_assets - excluded_vehicle, 0)
