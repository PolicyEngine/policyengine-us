from policyengine_us.model_api import *


class nyc_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "NYC refundable credits"
    unit = USD
    definition_period = YEAR
    defined_for = "in_nyc"
    reference = "https://www.tax.ny.gov/pit/credits/new_york_city_credits.htm#:~:text=New%20for%202022,adjusted%20gross%20income%20(NYAGI)."

    adds = "gov.local.ny.nyc.tax.income.credits.refundable"
