from policyengine_us.model_api import *


class savers_credit(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    uprating = "calibration.gov.cbo.income_by_source.adjusted_gross_income"
    label = "Retirement Savings Credit"
    unit = USD
    reference = (
        "https://www.irs.gov/pub/irs-pdf/f8880.pdf",
        "https://www.law.cornell.edu/uscode/text/26/25B#c",
    )

    adds = ["savers_credit_person"]
