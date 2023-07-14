from policyengine_us.model_api import *


class nm_agi(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Mexico AGI"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://klvg4oyd4j.execute-api.us-west-2.amazonaws.com/prod/PublicFiles/34821a9573ca43e7b06dfad20f5183fd/2f1a6781-9534-4436-b427-1557f9592099/2022pit-adj-ins.pdf",
    )
    defined_for = StateCode.NM
    
    adds = ["adjusted_gross_income", "nm_agi_additions"]
    
    subtracts = [
        "tax_exempt_interest_income", # Line 6
        "dividend_income", # Line 6
        "us_govt_interest", # Line 8
        "tax_unit_taxable_social_security",  # includes railroad retirement benefits, Line 9, Line 24
        "nm_aged_blind_exemption", # Line 12
        "nm_mediacal_care_expense_deduction", # Line 13/17?
        "investment_in_529_plan", # Line14
        "military_service_income", # Line 16
        "nm_itemized_deductions" # Line 20
    ]
