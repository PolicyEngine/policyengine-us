from openfisca_us.model_api import *


class used_clean_vehicle_credit(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Used clean vehicle credit"
    documentation = "Nonrefundable credit for the purchase of a previously-owned clean vehicle"
    unit = USD
    reference = "https://www.democrats.senate.gov/imo/media/doc/inflation_reduction_act_of_2022.pdf#page=370"
    defined_for = "used_clean_vehicle_credit_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.irs.credits.clean_vehicle.used
        sale_price = tax_unit("used_clean_vehicle_sale_price", period)
        # Amount is lesser of $4,000 and 30% of sale price.
        uncapped_amount = sale_price * p.amount.percent_of_sale_price
        return min_(uncapped_amount, p.amount.max)
