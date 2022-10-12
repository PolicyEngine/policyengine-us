from policyengine_us.model_api import *


class used_clean_vehicle_credit_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    definition_period = YEAR
    label = "Eligible for used clean vehicle credit"
    documentation = "Eligible for nonrefundable credit for the purchase of a previously-owned clean vehicle"
    unit = USD
    reference = "https://www.democrats.senate.gov/imo/media/doc/inflation_reduction_act_of_2022.pdf#page=370"
    defined_for = "purchased_qualifying_used_clean_vehicle"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.irs.credits.clean_vehicle.used
        # Income eligibility based on lesser of MAGI in current and prior year.
        # Assume AGI in current year for now.
        agi = tax_unit("adjusted_gross_income", period)
        filing_status = tax_unit("filing_status", period)
        income_limit = p.eligibility.income_limit[filing_status]
        income_eligible = agi <= income_limit
        # Purchase price limit.
        sale_price = tax_unit("used_clean_vehicle_sale_price", period)
        price_eligible = sale_price <= p.eligibility.sale_price_limit
        return income_eligible & price_eligible
