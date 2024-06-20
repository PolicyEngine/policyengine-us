from policyengine_us.model_api import *


class ctc_social_security_excess(Variable):
    value_type = float
    entity = TaxUnit
    label = "Refundable Child Tax Credit Social Security Excess"
    unit = USD
    documentation = (
        "The excess amount in social security for child tax credit calculation"
    )
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/24#d_2"

    adds = "gov.irs.credits.ctc.refundable.ss_add"
    subtracts = "gov.irs.credits.ctc.refundable.ss_subtract"
