from policyengine_us.model_api import *


class tn_ff_countable_resources(Variable):
    value_type = float
    entity = SPMUnit
    label = "Tennessee Families First countable resources"
    unit = USD
    definition_period = MONTH
    reference = "https://publications.tnsosfiles.com/rules/1240/1240-01/1240-01-50.20081124.pdf#page=1"
    defined_for = StateCode.TN

    def formula(spm_unit, period, parameters):
        cash_assets = spm_unit("spm_unit_cash_assets", period.this_year)
        vehicle_value = spm_unit.household("household_vehicles_value", period.this_year)
        p = parameters(period).gov.states.tn.dhs.ff.resources
        countable_vehicle_value = max_(vehicle_value - p.vehicle_exemption, 0)
        return cash_assets + countable_vehicle_value
