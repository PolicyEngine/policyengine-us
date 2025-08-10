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
            return potential
        else:
            return min_(credit_limit, potential)
