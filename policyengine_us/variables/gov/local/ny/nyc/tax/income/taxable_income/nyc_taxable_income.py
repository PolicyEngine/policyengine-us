from policyengine_us.model_api import *


class nyc_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "NYC taxable income"
    unit = USD
    definition_period = YEAR
    defined_for = "in_nyc"
    reference = "https://www.tax.ny.gov/pdf/2022/printable-pdfs/inc/it201i-2022.pdf#page=16"
    adds = ["ny_taxable_income"]
    # If had contribution(s) to Charitable Gifts Trust Fund accounts AND
    # itemized those contributions, would subtract the contribution(s)
    # amount from their NY AGI and the their itemized deduction amount.
    # Otherwise, enter New York State taxable income.from policyengine_us.model_api import *
    # We don't model those contributions, so just enter state taxable income.
