from policyengine_us.model_api import *


class md_local_income_tax_before_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD local income tax before refundable credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MD
    reference = "https://www.marylandcomptroller.gov/content/dam/mdcomp/tax/instructions/2025/resident-booklet.pdf#page=26"
    adds = ["md_local_income_tax_before_credits"]
    subtracts = ["md_local_eitc", "md_local_poverty_line_credit"]
