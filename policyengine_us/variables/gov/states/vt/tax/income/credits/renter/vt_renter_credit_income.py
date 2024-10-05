from policyengine_us.model_api import *


class vt_renter_credit_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Vermont renter credit income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://law.justia.com/codes/vermont/2022/title-32/chapter-154/section-6061/",  # (18)
        "https://tax.vermont.gov/sites/tax/files/documents/Income%20Booklet-2022.pdf#page=36",
    )
    defined_for = StateCode.VT

    adds = [
        "adjusted_gross_income",
        "vt_renter_credit_countable_tax_exempt_ss",
        "tax_exempt_interest_income",
    ]
