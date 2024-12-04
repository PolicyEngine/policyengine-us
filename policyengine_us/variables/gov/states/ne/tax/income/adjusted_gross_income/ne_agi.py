from policyengine_us.model_api import *


class ne_agi(Variable):
    value_type = float
    entity = TaxUnit
    label = "NE AGI"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://revenue.nebraska.gov/files/doc/tax-forms/2021/f_1040n_booklet.pdf"
        "https://revenue.nebraska.gov/files/doc/2022_Ne_Individual_Income_Tax_Booklet_8-307-2022_final_5.pdf"
    )
    defined_for = StateCode.NE
    adds = ["adjusted_gross_income", "ne_additions"]
    subtracts = ["ne_agi_subtractions"]
