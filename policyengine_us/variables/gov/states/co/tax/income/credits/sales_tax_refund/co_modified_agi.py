from policyengine_us.model_api import *


class co_modified_agi(Variable):
    value_type = float
    entity = TaxUnit
    label = "Colorado modified adjusted gross income for the sales tax refund"
    unit = USD
    definition_period = YEAR
    reference = "https://tax.colorado.gov/sites/tax/files/documents/DR_0104_Book_2022.pdf#page=23"
    defined_for = StateCode.CO

    adds = "gov.states.co.tax.income.credits.sales_tax_refund.magi_sources"
