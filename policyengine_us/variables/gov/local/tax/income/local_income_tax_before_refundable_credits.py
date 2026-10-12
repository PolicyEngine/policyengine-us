from policyengine_us.model_api import *


class local_income_tax_before_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Local income tax before refundable credits"
    documentation = "Local income, wage, and earnings taxes before refundable credits."
    unit = USD

    adds = [
        "nyc_income_tax_before_refundable_credits",
        "md_local_income_tax_before_refundable_credits",
        "in_county_tax",
        "or_multnomah_pfa_tax",
        "pa_philadelphia_wage_tax",
        "mo_kansas_city_earnings_tax",
        "mo_st_louis_earnings_tax",
        "ny_yonkers_income_tax",
        "de_wilmington_earned_income_tax",
    ]
