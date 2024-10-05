from policyengine_us.model_api import *


class ny_cdcc(Variable):
    value_type = float
    entity = TaxUnit
    label = "NY CDCC"
    unit = USD
    definition_period = YEAR
    reference = "https://www.nysenate.gov/legislation/laws/TAX/606"  # (c)
    defined_for = StateCode.NY

    def formula(tax_unit, period, parameters):
        cdcc_max = tax_unit("ny_cdcc_max", period)
        expenses = tax_unit("cdcc_relevant_expenses", period)
        cdcc_rate = tax_unit("ny_cdcc_rate", period) * tax_unit(
            "cdcc_rate", period
        )
        return min_(cdcc_max, expenses * cdcc_rate)
