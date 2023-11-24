from policyengine_us.model_api import *


class mt_other_additions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montana additions except addition to federal taxable social security benefits"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://mtrevenue.gov/wp-content/uploads/dlm_uploads/2023/05/Montana-Idividiual-Income-Tax-Return-Form-2-2022v6.2.pdf#page=4",
        "",
    )
    defined_for = StateCode.MT
    adds = ["tax_exempt_dividend_income"]
