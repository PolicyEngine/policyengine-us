from policyengine_us.model_api import *


class nh_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Hampshire taxable income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.gencourt.state.nh.us/rsa/html/V/77/77-4.htm",
        "https://www.revenue.nh.gov/forms/2023/documents/dp-10-2022-print.pdf",
    )
    defined_for = StateCode.NH

    # New Hampshire allows for negative taxable income.
    # It limits tax to nonnegative values in the tax computation instead.
    adds = ["dividend_income", "interest_income"]
    subtracts = ["nh_total_exemptions"]
