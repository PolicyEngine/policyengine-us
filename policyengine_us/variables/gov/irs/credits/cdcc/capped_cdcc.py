from policyengine_us.model_api import *


class capped_cdcc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Capped child/dependent care credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.irs.gov/pub/irs-prior/i2441--2021.pdf#page=1",
        "https://www.irs.gov/instructions/i2441#en_US_2022_publink1000106356",
        "https://www.law.cornell.edu/uscode/text/26/30D#c_2",
    )

    def formula(tax_unit, period, parameters):
        cdcc = tax_unit("cdcc", period)
        p = parameters(period).gov.irs.credits
        if "cdcc" in p.refundable:
            return cdcc
        # follow Credit Limit Worksheet in 2022 Form 2441 instructions:
        itaxbc = tax_unit("income_tax_before_credits", period)  # WS Line1
        # Excess Advance PTC Repayment (Form 8962) assumed zero in above line
        offset = tax_unit("foreign_tax_credit", period)
        # Partner Additional Reporting Year Tax (Form 8978) assumed zero above
        cap = max_(itaxbc - offset, 0)  # WS Line 2
        return min_(cdcc, cap)  # WS Line 3
