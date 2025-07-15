from policyengine_us.model_api import *


class new_clean_vehicle_credit_credit_limit(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "New clean vehicle credit credit limit"
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
        income_tax_before_credits = tax_unit(
            "income_tax_before_credits", period
        )
        p = parameters(period).gov.irs.credits.clean_vehicle.new
        preceding_credits = add(tax_unit, period, p.preceding_credits)
        return max_(income_tax_before_credits - preceding_credits, 0)
