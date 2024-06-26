from policyengine_us.model_api import *

class nyserda_ny_drive_clean_rebate(Variable):
    value_type = float
    entity = TaxUnit # TODO: Check if this is right. Not a tax credit.
    label = "NY Drive Clean Rebate"
    unit = USD
    definition_period = YEAR
    reference = "https://www.nyserda.ny.gov/All-Programs/Drive-Clean-Rebate-For-Electric-Cars-Program"
    defined_for = StateCode.NY

    def formula(tax_unit, parameters, period):
        p = parameters(period).parameters.gov.states.ny.nyserda.drive_clean
        # Calculate vehicle all-electric range
        vehicle_range = tax_unit("nyserda_drive_clean_vehicle_electric_range", period)
        # Calculate vehicle price
        vehicle_cost = tax_unit("nyserda_drive_clean_vehicle_cost", period)
        # Calculate rebate size based on range 
        rebate_amount_based_on_range = p.amount.calc(vehicle_range)
        # Determine whether or not vehicle is over the MSRP threhold and qualifies for the flat rebate
        vehicle_over_msrp_threshold = vehicle_cost >= p.flat_rebate.msrp_threshold
        flat_amount = p.flat_rebate.amount
        # If the vehicle is more expensive than the MSRP treshold it receives the flat rebate, otherwise it receives the range-based rebate
        return np.where(vehicle_over_msrp_threshold, flat_amount, rebate_amount_based_on_range)