from policyengine_us.model_api import *


class tax_exempt_pension_income(Variable):
    value_type = float
    entity = Person
    label = "tax-exempt pension income"
    unit = USD
    definition_period = YEAR
    uprating = "calibration.gov.cbo.income_by_source.adjusted_gross_income"

    adds = [
        "tax_exempt_public_pension_income",
        "tax_exempt_private_pension_income",
    ]
