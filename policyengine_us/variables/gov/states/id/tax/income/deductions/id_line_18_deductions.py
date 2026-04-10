from policyengine_us.model_api import *


class id_line_18_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Idaho Form 40 line 18 deductions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.ID
    reference = (
        "https://tax.idaho.gov/wp-content/uploads/forms/EIN00046/EIN00046_03-02-2026.pdf",
        "https://tax.idaho.gov/pressrelease/update-on-filing-2025-idaho-income-taxes-now-that-conformity-is-law/",
    )

    adds = [
        "qualified_business_income_deduction",
        "id_additional_senior_deduction",
    ]
