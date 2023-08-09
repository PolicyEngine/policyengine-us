from policyengine_us.model_api import *


class va_refundable_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Virginia refundable EITC"
    unit = USD
    documentation = (
        "Refundable EITC credit reducing VA State income tax page 26."
    )
    definition_period = YEAR
    reference = "https://www.tax.virginia.gov/sites/default/files/vatax-pdf/2022-760-instructions.pdf#page=26"
    defined_for = "va_claims_refundable_eitc"

    adds = ["va_refundable_eitc_if_claimed"]
