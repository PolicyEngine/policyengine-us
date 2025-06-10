from policyengine_us.model_api import *


class new_clean_vehicle_credit(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "New clean vehicle credit"
    documentation = (
        "Nonrefundable credit for the purchase of a new clean vehicle"
    )
    unit = USD
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/30D",
        "https://www.democrats.senate.gov/imo/media/doc/inflation_reduction_act_of_2022.pdf#page=373",
    )
    defined_for = "new_clean_vehicle_credit_eligible"

    def formula(tax_unit, period, parameters):
        credit_limit = tax_unit(
            "new_clean_vehicle_credit_credit_limit", period
        )
        potential = tax_unit("new_clean_vehicle_credit_potential", period)
        return min_(credit_limit, potential)
