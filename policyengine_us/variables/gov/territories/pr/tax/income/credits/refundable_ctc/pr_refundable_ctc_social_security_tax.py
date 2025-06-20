from policyengine_us.model_api import *


class pr_refundable_ctc_social_security_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Puerto Rico social security and medicare taxes for refundable Child Tax Credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.irs.gov/pub/irs-pdf/f1040s8.pdf"
        "https://www.law.cornell.edu/uscode/text/26/24#h_4_A"
    )

    # line 23
    adds = "gov.irs.credits.ctc.refundable.social_security.add"
