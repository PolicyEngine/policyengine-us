from policyengine_us.model_api import *


class nyc_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "NYC taxable income"
    unit = USD
    definition_period = YEAR
    defined_for = "in_nyc"

    def formula(tax_unit, period, parameters):
        # If had contribution(s) to Charitable Gifts Trust Fund accounts AND
        # itemized those contributions, would subtract the contribution(s)
        # amount from their NY AGI and the their itemized decudtion amount.
        # https://www.tax.ny.gov/pdf/2022/printable-pdfs/inc/it201i-2022.pdf#page=16

        # First get their NY AGI.
        agi = tax_unit("ny_agi", period)

        deductions_and_exemptions = add(
            tax_unit,
            period,
            ["nyc_taxable_income_deductions", "nyc_exemptions"],
        )

        return max_(agi - deductions_and_exemptions, 0)
