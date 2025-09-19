from policyengine_us.model_api import *
from policyengine_us.tools.general import select_filing_status_value


class ny_inflation_refund_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "New York 2025 inflation refund credits"
    unit = USD
    definition_period = YEAR
    reference = "https://www.nysenate.gov/legislation/laws/TAX/606#QQQ"
    defined_for = StateCode.NY

    def formula(tax_unit, period, parameters):
        return 0

    def formula_2025(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.ny.tax.income.credits.inflation_refund
        agi = tax_unit("ny_agi", period)
        filing_status = tax_unit("filing_status", period)

        return select_filing_status_value(
            filing_status,
            p,
            agi,
            right=True,
        )

    def formula_2026(tax_unit, period, parameters):
        return 0
