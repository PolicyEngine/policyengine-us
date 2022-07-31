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
        p = parameters(period).gov.irs.credits.electric_vehicle.new
        # Amount per kWh of EV battery capacity.
        # "In the case of a vehicle which draws propulsion energy from a
        # battery with not less than 5 kilowatt hours of capacity, the amount
        # determined under this paragraph is $417, plus $417 for each kilowatt
        #  hour of capacity in excess of 5 kilowatt hours."
        capacity = tax_unit("new_electric_vehicle_battery_capacity", period)
        kwh_excess = max_(capacity - p.capacity_bonus.kwh_threshold + 1, 0)
        kwh_bonus = min_(
            p.capacity_bonus.amount * np.floor(kwh_excess),
            p.capacity_bonus.max,
        )
        return p.base_amount + kwh_bonus
