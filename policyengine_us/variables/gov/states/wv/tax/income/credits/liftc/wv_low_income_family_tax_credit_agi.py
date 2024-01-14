from policyengine_us.model_api import *


class wv_low_income_family_tax_credit_agi(Variable):
    value_type = float
    entity = TaxUnit
    label = "Adjusted gross income for the West Virginia low-income family tax credit"
    unit = USD
    definition_period = YEAR
    reference = "https://code.wvlegislature.gov/11-21-12/"  # §11-21-12 (b)
    defined_for = "wv_low_income_family_tax_credit_eligible"

    adds = [
        "adjusted_gross_income",
        "tax_exempt_interest_income",
        "wv_additions",
    ]
