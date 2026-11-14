from policyengine_us.model_api import *


class federal_scholarship_tax_credit_carryforward_2(Variable):
    value_type = float
    entity = TaxUnit
    label = "Federal Scholarship Tax Credit carry-in from 2 prior taxable year(s)"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Valid unused credit arising exactly 2 taxable year(s) before the current "
        "year, net of intervening use. Supply historical balances explicitly. "
        "TaxUnit membership remains fixed; the caller supplies valid allocations "
        "after any filing-unit change. This input does not invent prior donations."
    )
    reference = "https://uscode.house.gov/us/usc/t26/s25F/"
