from policyengine_us.model_api import *


class medicaid_medically_needy_medical_expenses(Variable):
    value_type = float
    entity = Person
    label = "Medicaid medically needy medical expenses"
    unit = USD
    documentation = (
        "Medical expenses used for Medicaid medically needy spenddown. "
        "Includes employee-paid health insurance premiums from pretax payroll "
        "deductions and disjoint non-pretax amounts, excluding expenses payable "
        "by third parties."
    )
    definition_period = YEAR
    reference = (
        "https://www.ecfr.gov/current/title-42/section-435.831#p-435.831(d)",
        "https://www.ecfr.gov/current/title-42/section-435.831#p-435.831(e)(1)",
    )

    adds = [
        "medical_expense_health_insurance_premiums",
        "pre_tax_health_insurance_premiums",
        "other_medical_expenses",
    ]
