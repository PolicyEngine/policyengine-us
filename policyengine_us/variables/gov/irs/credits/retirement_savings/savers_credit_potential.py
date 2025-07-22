from policyengine_us.model_api import *


class savers_credit_potential(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Potential value of the Retirement Savings Credit"
    unit = USD
    reference = (
        "https://www.irs.gov/pub/irs-pdf/f8880.pdf",
        "https://www.law.cornell.edu/uscode/text/26/25B#c",
    )

    adds = ["savers_credit_person"]
