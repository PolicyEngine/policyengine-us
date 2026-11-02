from policyengine_us.model_api import *


class ny_interest_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "New York interest deduction"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Interest New York allows as an itemized deduction: the federal "
        "interest_deduction components, with New York's pre-TCJA home "
        "mortgage interest in place of the federal home mortgage interest."
    )
    reference = (
        "https://www.nysenate.gov/legislation/laws/TAX/615",
        "https://www.tax.ny.gov/pit/file/itemized-deductions-2025.htm#interest",
    )
    defined_for = StateCode.NY

    adds = [
        "ny_mortgage_interest_deduction",
        "non_mortgage_interest",
        "deductible_mortgage_insurance_premiums",
    ]
