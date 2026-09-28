from policyengine_us.model_api import *


class self_employment_gross_income(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    unit = USD
    # Receipts before business expenses, including farm and non-farm businesses.
    label = "Gross self-employment receipts"
    reference = (
        "https://www.irs.gov/instructions/i1040sc",
        "https://www.irs.gov/instructions/i1040sf",
    )
