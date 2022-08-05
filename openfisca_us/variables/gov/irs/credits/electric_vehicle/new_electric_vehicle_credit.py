from openfisca_us.model_api import *
import numpy as np


class new_electric_vehicle_credit(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "New electric vehicle credit"
    documentation = (
        "Nonrefundable credit for the purchase of a new electric vehicle"
    )
    unit = USD
    reference = "https://www.law.cornell.edu/uscode/text/26/30D"
    defined_for = "new_electric_vehicle_credit_eligible"

    def formula(tax_unit, period, parameters):
        ira = parameters(
            period
        ).contrib.congress.senate.democrats.inflation_reduction_act
        # The Inflation Reduction Act changes the credit structure.
        if ira.in_effect:
            p = ira.electric_vehicle_credit.new
            battery_component_percent = tax_unit(
                "new_electric_vehicle_battery_components_made_in_north_america",
                period,
            )
            meets_battery_component_test = (
                battery_component_percent >= p.battery_components.threshold
            )
            critical_minerals_percent = tax_unit(
                "new_electric_vehicle_battery_critical_minerals_extracted_in_trading_partner_country",
                period,
            )
            meets_critical_minerals_test = (
                critical_minerals_percent >= p.critical_minerals.threshold
            )
            battery_components_credit = (
                meets_battery_component_test * p.battery_components.amount
            )
            critical_minerals_credit = (
                meets_critical_minerals_test * p.critical_minerals.amount
            )
            return battery_components_credit + critical_minerals_credit
        # Otherwise compute under current law.
        p = parameters(period).gov.irs.credits.electric_vehicle.new
        # Amount per kWh of EV battery capacity.
        # "In the case of a vehicle which draws propulsion energy from a
        # battery with not less than 5 kilowatt hours of capacity, the amount
        # determined under this paragraph is $417, plus $417 for each kilowatt
        # hour of capacity in excess of 5 kilowatt hours."
        capacity = tax_unit("new_electric_vehicle_battery_capacity", period)
        kwh_excess = max_(capacity - p.capacity_bonus.kwh_threshold + 1, 0)
        kwh_bonus = min_(
            p.capacity_bonus.amount * np.floor(kwh_excess),
            p.capacity_bonus.max,
        )
        return p.base_amount + kwh_bonus
