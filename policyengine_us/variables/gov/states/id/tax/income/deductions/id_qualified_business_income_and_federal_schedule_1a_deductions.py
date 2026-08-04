from policyengine_us.model_api import *


class id_qualified_business_income_and_federal_schedule_1a_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Idaho qualified business income and federal Schedule 1-A deductions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.ID
    reference = (
        "https://tax.idaho.gov/wp-content/uploads/forms/EIN00046/EIN00046_03-02-2026.pdf#page=11",
        "https://tax.idaho.gov/pressrelease/update-on-filing-2025-idaho-income-taxes-now-that-conformity-is-law/",
    )

    adds = (
        "gov.states.id.tax.income.deductions"
        ".qualified_business_income_and_federal_schedule_1a_deductions"
    )
