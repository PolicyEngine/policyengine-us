from policyengine_us.model_api import *


class ne_refundable_ctc_total_household_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Nebraska refundable Child Tax Credit total household income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://nebraskalegislature.gov/laws/statutes.php?statute=77-7203",
        "https://revenue.nebraska.gov/businesses/child-care-tax-credit-act",
    )
    defined_for = StateCode.NE

    def formula(tax_unit, period, parameters):
        return tax_unit("adjusted_gross_income", period)
