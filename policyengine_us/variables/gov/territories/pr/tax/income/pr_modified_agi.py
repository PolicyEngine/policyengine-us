from policyengine_us.model_api import *


class pr_modified_agi(Variable):
    value_type = float
    entity = TaxUnit
    label = "Puerto Rico modified adjusted gross income for the additional child tax credit"
    unit = USD
    definition_period = YEAR
    reference = ""

    #adds = "gov.states.co.tax.income.credits.sales_tax_refund.magi_sources"
