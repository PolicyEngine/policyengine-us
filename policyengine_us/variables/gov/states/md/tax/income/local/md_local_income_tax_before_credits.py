from policyengine_us.model_api import *


class md_local_income_tax_before_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD local income tax before credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MD
    reference = "https://www.marylandcomptroller.gov/content/dam/mdcomp/tax/instructions/2025/resident-booklet.pdf#page=25"
    adds = [
        "md_anne_arundel_county_tax",
        "md_frederick_county_tax",
        "md_flat_rate_county_tax",
    ]
