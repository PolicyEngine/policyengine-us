from policyengine_us.model_api import *


class amt_base_tax(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Alternative Minimum Tax base tax"
    unit = USD
    documentation = "Alternative Minimum Tax (AMT) base tax, Form 6251 Part II Line 7 'All Others'"
    reference = "https://www.irs.gov/pub/irs-pdf/f6251.pdf"

    adds = [
        "amt_lower_base_tax",
        "amt_higher_base_tax",
    ]
