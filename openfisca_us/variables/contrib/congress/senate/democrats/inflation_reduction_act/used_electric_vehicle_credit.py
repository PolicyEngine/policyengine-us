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
        p = parameters(
            period
        ).contrib.congress.senate.democrats.inflation_reduction_act.electric_vehicle_credit.used
        # Income eligibility based on lesser of MAGI in current and prior year.
        # Assume AGI in current year for now.
        agi = tax_unit("adjusted_gross_income", period)
        filing_status = tax_unit("filing_status", period)
        income_limit = p.eligibility.income_limit[filing_status]
        income_eligible = agi <= income_limit
        # Purchase price limit.
        sale_price = tax_unit("used_electric_vehicle_sale_price", period)
        price_eligible = price <= p.eligibility.sale_price_limit
        # Amount is lesser of $4,000 and 30% of sale price.
        uncapped_amount = sale_price * p.amount.percent_of_sale_price
        amount_if_eligible = min_(uncapped_amount, p.amount.max)
        return income_eligible * price_eligible * amount_if_eligible
