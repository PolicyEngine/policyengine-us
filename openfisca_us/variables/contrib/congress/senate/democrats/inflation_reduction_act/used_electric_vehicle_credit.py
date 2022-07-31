from openfisca_us.model_api import *


class used_electric_vehicle_credit(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Used electric vehicle credit"
    documentation = (
        "Nonrefundable credit for the purchase of a used electric vehicle"
    )
    unit = USD
    reference = "https://www.democrats.senate.gov/imo/media/doc/inflation_reduction_act_of_2022.pdf#page=370"

    def formula(tax_unit, period, parameters):
        return 0
