from policyengine_us.model_api import *


class cdcc_limit(Variable):
    value_type = float
    entity = TaxUnit
    label = "CDCC-relevant care expense limit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/21#c",
        "https://www.law.cornell.edu/uscode/text/26/21#d_1",
    )

    def formula(tax_unit, period, parameters):
        cdcc = parameters(period).gov.irs.credits.cdcc
        capped_count_cdcc_eligible = tax_unit(
            "capped_count_cdcc_eligible", period
        )
        return cdcc.max * capped_count_cdcc_eligible
