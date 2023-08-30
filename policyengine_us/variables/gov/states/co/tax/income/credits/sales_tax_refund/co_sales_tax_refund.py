from policyengine_us.model_api import *


class co_sales_tax_refund(Variable):
    value_type = float
    entity = TaxUnit
    label = "Colorado sales tax refund"
    unit = USD
    definition_period = YEAR
    reference = "https://tax.colorado.gov/sites/tax/files/documents/DR_0104_Book_2022.pdf#page=23"
    defined_for = "co_sales_tax_refund_eligible"

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        status = filing_status.possible_values
        p = parameters(
            period
        ).gov.states.co.tax.income.credits.sales_tax_refund.amount
        agi = tax_unit("co_modified_agi", period)
        multiplier = p.multiplier[filing_status]
        amount = p.base.calc(agi)
        return multiplier * amount
