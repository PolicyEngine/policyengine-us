from policyengine_us.model_api import *


class nh_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Hampshire taxable income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://gc.nh.gov/rsa/html/V/77/77-mrg.htm",
        "https://www.revenue.nh.gov/sites/g/files/ehbemt736/files/documents/dp-10-2022-print.pdf",
    )
    defined_for = StateCode.NH

    def formula(tax_unit, period, parameters):
        # The head's and spouse's interest and dividends: a tax unit dependent
        # is a separate individual who reports their own on their own return.
        income = tax_unit_non_dep_add(
            tax_unit, period, ["dividend_income", "interest_income"]
        )
        # New Hampshire allows for negative taxable income.
        # It limits tax to nonnegative values in the tax computation instead.
        return income - tax_unit("nh_total_exemptions", period)
