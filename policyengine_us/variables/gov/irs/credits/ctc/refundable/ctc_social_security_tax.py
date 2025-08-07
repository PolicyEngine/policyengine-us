from policyengine_us.model_api import *


class ctc_social_security_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Refundable Child Tax Credit Social Security Tax"
    unit = USD
    documentation = (
        "Social Security taxes considered in the Child Tax Credit calculation"
    )
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/24#d_2"

    adds = "gov.irs.credits.ctc.refundable.social_security.add"
    subtracts = "gov.irs.credits.ctc.refundable.social_security.subtract"
