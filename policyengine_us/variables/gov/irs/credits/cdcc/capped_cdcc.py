from policyengine_us.model_api import *


class capped_cdcc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Capped Child/dependent care credit"
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
        # The cdcc is capped at the amount of Form 1040, line 18 if non-refundable
        tax_before_credits = tax_unit("regular_tax_before_credits", period)
        foreign_tax_credit = tax_unit("foreign_tax_credit", period)
        # The tax before credits amount is also reduced by the Partner’s Additional Reporting Year Tax
        # which is currently not implemented
        cap = max_(tax_before_credits - foreign_tax_credit, 0)
        return min_(cdcc, cap)
