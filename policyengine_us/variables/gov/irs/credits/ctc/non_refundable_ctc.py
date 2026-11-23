from policyengine_us.model_api import *


class non_refundable_ctc(Variable):
    value_type = float
    entity = TaxUnit
    label = "non-refundable CTC"
    unit = USD
    documentation = (
        "The nonrefundable Child Tax Credit entitlement before the section "
        "26(a) tax-liability limit. In 2021 this is the credit for other "
        "dependents on Schedule 8812 line 14a, before the limit on line 14d."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/26#a",
        "https://www.irs.gov/pub/irs-prior/f1040s8--2021.pdf#page=1",
    )
    adds = ["ctc"]
    subtracts = ["refundable_ctc"]
