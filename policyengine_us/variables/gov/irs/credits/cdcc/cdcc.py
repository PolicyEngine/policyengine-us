from policyengine_us.model_api import *


class cdcc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Child/dependent care credit"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/21"

    def formula(tax_unit, period, parameters):
        credit_limit = tax_unit("cdcc_credit_limit", period)
        potential = tax_unit("cdcc_potential", period)
        # In 2021, the CDCC was refundable
        p = parameters(period).gov.irs.credits
        if "cdcc" in p.refundable:
            credit = potential
        else:
            credit = min_(credit_limit, potential)
        # IRC 21(e)(2): a married taxpayer may claim the credit only on a joint
        # return. A separated taxpayer who qualifies under 21(e)(4) is treated
        # as not married and files as head of household, not separately.
        filing_status = tax_unit("filing_status", period)
        separate = filing_status == filing_status.possible_values.SEPARATE
        return where(separate, 0, credit)
