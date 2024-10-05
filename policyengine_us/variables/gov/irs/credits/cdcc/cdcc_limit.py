from policyengine_us.model_api import *


class cdcc_limit(Variable):
    value_type = float
    entity = TaxUnit
    label = "CDCC-relevant care expense limit"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/21#c"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.irs.credits.cdcc
        capped_count_cdcc_eligible = tax_unit(
            "capped_count_cdcc_eligible", period
        )
        return p.max * capped_count_cdcc_eligible
