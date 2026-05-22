from policyengine_us.model_api import *


class itemized_medical_expenses(Variable):
    value_type = float
    entity = TaxUnit
    label = "Itemized medical expenses"
    unit = USD
    definition_period = YEAR
    reference = [
        "https://www.law.cornell.edu/uscode/text/26/213#a",
        "https://www.law.cornell.edu/uscode/text/26/213#d_1",
    ]
    documentation = (
        "Medical expenses counted before applying the itemized medical "
        "expense deduction floor. IRC Section 213(d)(1) defines medical care "
        "to include amounts paid for diagnosis, cure, mitigation, treatment, "
        "or prevention of disease; transportation primarily for essential "
        "medical care; qualified long-term care services; and insurance "
        "premiums covering medical care. Current modeling uses health "
        "insurance premiums and other medical expenses, excluding general "
        "over-the-counter health expenses."
    )

    adds = [
        "medical_expense_health_insurance_premiums",
        "other_medical_expenses",
    ]
