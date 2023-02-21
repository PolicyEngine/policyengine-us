from policyengine_us.model_api import *


class nyc_non_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "NYC non-refundable tax credits"
    unit = USD
    definition_period = YEAR
    reference = "https://www.tax.ny.gov/pit/credits/new_york_city_credits.htm#:~:text=New%20for%202022,adjusted%20gross%20income%20(NYAGI)."

    # This was the forumla for ny_non_refundable_credits
    # def formula(tax_unit, period, parameters):
    #     credits = parameters(
    #         period
    #     ).gov.states.ny.tax.income.credits.non_refundable
    #     income_tax = tax_unit("ny_income_tax_before_credits", period)
    #     total_credit_value = add(tax_unit, period, credits)
    #     return min_(income_tax, total_credit_value)

    # This is what I think it should be.
    adds = [
        "nyc_household_credit",
        "nyc_unincorporated_business_credit",
    ]
