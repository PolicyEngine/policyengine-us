from policyengine_us.model_api import *


class ny_cdcc(Variable):
    value_type = float
    entity = TaxUnit
    label = "NY CDCC"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.nysenate.gov/legislation/laws/TAX/606",  # (c)
        "https://www.tax.ny.gov/pdf/current_forms/it/it216i.pdf#page=1",
    )
    defined_for = StateCode.NY

    def formula(tax_unit, period, parameters):
        cdcc_max = tax_unit("ny_cdcc_max", period)
        expenses = tax_unit("cdcc_relevant_expenses", period)
        cdcc_rate = tax_unit("ny_cdcc_rate", period) * tax_unit("cdcc_rate", period)
        # Form IT-216 requires qualifying for the federal credit and applies
        # the IRC §21(e)(2) and (4) special rules, so a married filer must
        # file jointly unless treated as unmarried.
        eligible = tax_unit("cdcc_filing_status_eligible", period)
        return eligible * min_(cdcc_max, expenses * cdcc_rate)
