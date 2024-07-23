from policyengine_us.model_api import *


class ny_drive_clean_rebate(Variable):
    value_type = float
    entity = Household
    label = "New York Drive Clean Rebate"
    unit = USD
    definition_period = YEAR
    reference = "https://www.nyserda.ny.gov/-/media/Project/Nyserda/Files/Programs/Drive-Clean-NY/implementation-manual.pdf#page=8"
    defined_for = StateCode.NY

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ny.nyserda.drive_clean
        # Calculate vehicle all-electric range
        vehicle_range = tax_unit(
            "ny_drive_clean_vehicle_electric_range", period
        )
        # Calculate vehicle price
        vehicle_cost = tax_unit("ny_drive_clean_vehicle_cost", period)
        # Calculate rebate size based on range
        rebate_amount_based_on_range = p.amount.calc(vehicle_range)
        # Determine whether or not vehicle is over the MSRP threhold,
        # qualifying for the flat rebate
        vehicle_over_msrp_threshold = (
            vehicle_cost >= p.flat_rebate.msrp_threshold
        )
        # If the vehicle is more expensive than the MSRP treshold, the filer
        # receives the flat rebate, otherwise they receive the range-based rebate
        return where(
            vehicle_over_msrp_threshold,
            p.flat_rebate.amount,
            rebate_amount_based_on_range,
        )
