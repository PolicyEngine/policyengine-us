from policyengine_us.model_api import *


class medicaid_medically_needy_medical_expenses(Variable):
    value_type = float
    entity = Person
    label = "Medicaid medically needy medical expenses"
    unit = USD
    documentation = "Medical expenses used for Medicaid medically needy spenddown."
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/cfr/text/42/part-435/subpart-D"

    adds = [
        "medical_expense_health_insurance_premiums",
        "other_medical_expenses",
    ]
