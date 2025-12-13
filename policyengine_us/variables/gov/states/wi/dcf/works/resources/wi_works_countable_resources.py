from policyengine_us.model_api import *


class wi_works_countable_resources(Variable):
    value_type = float
    entity = SPMUnit
    label = "Wisconsin Works countable resources"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://dcf.wisconsin.gov/manuals/w-2-manual/Production/03/03.3.4_COUNTING_ASSETS.htm",
        "https://docs.legis.wisconsin.gov/code/admin_code/dcf/101_199/101/09/3/b",
    )
    defined_for = StateCode.WI

    def formula(spm_unit, period, parameters):
        liquid_assets = spm_unit("spm_unit_cash_assets", period)
        vehicle_value = spm_unit.household("household_vehicles_value", period)
        p = parameters(period).gov.states.wi.dcf.works.asset
        countable_vehicle = max_(vehicle_value - p.vehicle_exclusion, 0)
        return liquid_assets + countable_vehicle
