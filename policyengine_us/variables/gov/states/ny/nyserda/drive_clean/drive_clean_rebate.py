from policyengine_us.model_api import *


class ny_drive_clean_rebate(Variable):
    value_type = float
    entity = TaxUnit # TODO: Check if this is right. Not a tax credit.
    label = "NY Drive Clean Rebate"
    unit = USD
    definition_period = YEAR
    reference = "https://www.nyserda.ny.gov/All-Programs/Drive-Clean-Rebate-For-Electric-Cars-Program"
    defined_for = StateCode.NY

    def formula(tax_unit, parameters, period):
        p = parameters(period).parameters.gov.states.ny.nyserda.drive_clean
        vehicle_cost = tax_unit("drive_clean_vehicle_cost", period)
        if vehicle_cost >= p.drive_clean_high_msrp:
            cost_rebate = p.drive_clean_high_msrp_rebate
            return cost_rebate
        else:
            vehicle_all_electric_range = tax_unit("drive_clean_vehicle_electric_range", period)
            range_rebate = p.rebate.calc(vehicle_all_electric_range)
            return range_rebate