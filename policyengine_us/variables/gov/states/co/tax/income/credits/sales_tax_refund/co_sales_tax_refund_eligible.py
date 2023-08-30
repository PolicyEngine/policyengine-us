from policyengine_us.model_api import *


class co_sales_tax_refund_eligible(Variable):
    value_type = float
    entity = TaxUnit
    label = "Eligible for the Colorado sales tax refund"
    unit = USD
    definition_period = YEAR
    reference = "https://tax.colorado.gov/sites/tax/files/documents/DR_0104_Book_2022.pdf#page=23"
    defined_for = StateCode.CO

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        p = parameters(period).gov.states.co.tax.income.credits.sales_tax_refund
        