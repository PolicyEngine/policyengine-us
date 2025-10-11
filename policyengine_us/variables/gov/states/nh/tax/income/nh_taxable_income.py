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

    # New Hampshire taxes ALL interest income, including federally tax-exempt
    # interest from other states' municipal bonds. Per RSA 77:4, the tax applies
    # to "Interest from bonds, notes, money at interest, and from all debts due
    # the person to be taxed" with exclusions only for NH state and local bonds.
    # This differs from federal taxation and from TAXSIM's implementation.
    adds = ["dividend_income", "interest_income"]
    subtracts = ["nh_total_exemptions"]
