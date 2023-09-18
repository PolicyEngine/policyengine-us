from policyengine_us.model_api import *


class mt_modified_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montana modified income for the taxable social security benefits"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://mtrevenue.gov/wp-content/uploads/mdocs/form%202%202021.pdf" ""
    )
    defined_for = StateCode.MT
    adds = [
        "mt_agi_additions",
        "tax_exempt_interest_income",
        "mt_modified_income_benefit_fraction",
        "student_loan_interest",
    ]
    subtracts = [
        "taxable_social_security",
        "interest_income",
        "mt_adjustments",
        "mt_agi_subtractions",
    ]
