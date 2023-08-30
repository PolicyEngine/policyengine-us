from policyengine_us.model_api import *


class co_sales_tax_refund(Variable):
    value_type = float
    entity = TaxUnit
    label = "Colorado sales tax refund"
    unit = USD
    definition_period = YEAR
    reference = "https://tax.colorado.gov/sites/tax/files/documents/DR_0104_Book_2022.pdf#page=23"
    defined_for = StateCode.CO

    def formula(tax_unit, period, parameters):
        