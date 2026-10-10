from policyengine_us.model_api import *


class estate_income_would_be_qualified(Variable):
    value_type = bool
    entity = Person
    label = "Estate and trust income would be qualified"
    documentation = (
        "Whether the estate and trust income amount consists of the beneficiary's "
        "allocated qualified business items reported on Form 1041 Schedule K-1, "
        "box 14, code I. Taxable estate or trust income alone does not establish "
        "QBI qualification."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/199A#c",
        "https://www.law.cornell.edu/uscode/text/26/662",
        "https://www.law.cornell.edu/cfr/text/26/1.199A-6#d",
        "https://www.irs.gov/pub/irs-pdf/i1041sk1.pdf#page=4",
    )
    default_value = False
