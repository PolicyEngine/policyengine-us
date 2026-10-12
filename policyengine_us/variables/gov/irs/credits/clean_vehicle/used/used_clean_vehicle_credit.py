from policyengine_us.model_api import *


class used_clean_vehicle_credit(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Used clean vehicle credit"
    documentation = (
        "Nonrefundable credit for the purchase of a previously-owned clean vehicle"
    )
    unit = USD
    reference = "https://www.democrats.senate.gov/imo/media/doc/inflation_reduction_act_of_2022.pdf#page=370"
    defined_for = "used_clean_vehicle_credit_eligible"

    def formula(tax_unit, period, parameters):
        # Form 8936, line 18: the smaller of the credit and the tax liability
        # limit; the unused credit is lost.
        credit_limit = tax_unit("used_clean_vehicle_credit_credit_limit", period)
        potential = tax_unit("used_clean_vehicle_credit_potential", period)
        return min_(credit_limit, potential)
