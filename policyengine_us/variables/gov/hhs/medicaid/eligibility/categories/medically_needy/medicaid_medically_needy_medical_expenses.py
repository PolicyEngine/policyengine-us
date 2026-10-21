from policyengine_us.model_api import *


class medicaid_medically_needy_medical_expenses(Variable):
    value_type = float
    entity = Person
    label = "Medicaid medically needy medical expenses"
    unit = USD
    documentation = (
        "Annual expense proxy for SSI-based Medicaid medically needy spenddown. "
        "Includes non-pretax health premiums and other medical expenses. "
        "Qualified pretax payroll premiums are excluded through SSI earnings "
        "rather than deducted again here. State-specific income and expense "
        "sequencing, including states using gross-income payroll deductions, "
        "is not modeled by this proxy."
    )
    definition_period = YEAR
    reference = (
        "https://www.ecfr.gov/current/title-42/section-435.831#p-435.831(d)",
        "https://www.ecfr.gov/current/title-42/section-435.831#p-435.831(e)(1)",
        "https://khap.kdhe.ks.gov/KEESM/July_2026_Output/7000/7500-Determination-of-Financial-Eligibility.htm",
    )

    adds = [
        "medical_expense_health_insurance_premiums",
        "other_medical_expenses",
    ]
