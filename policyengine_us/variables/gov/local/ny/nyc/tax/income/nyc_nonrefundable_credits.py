from policyengine_us.model_api import *


class nyc_non_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "NYC non-refundable tax credits"
    unit = USD
    definition_period = YEAR
    reference = "https://www.tax.ny.gov/pit/credits/new_york_city_credits.htm#:~:text=New%20for%202022,adjusted%20gross%20income%20(NYAGI)."
    defined_for = "in_nyc"

    adds = "gov.local.ny.nyc.tax.income.credits.non_refundable"
