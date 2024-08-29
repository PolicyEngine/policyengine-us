from policyengine_us.model_api import *


class ne_refundable_ctc_income_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Nebraska refundable Child Tax Credit total household income eligible child"
    definition_period = YEAR
    reference = (
        "https://nebraskalegislature.gov/laws/statutes.php?statute=77-7203",
        "https://revenue.nebraska.gov/businesses/child-care-tax-credit-act",
    )
    defined_for = StateCode.NE

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ne.tax.income.credits.ctc.refundable
        fpg = tax_unit("tax_unit_fpg", period)
        income_limit = fpg * p.fpg_fraction
        total_household_income = tax_unit(
            "ne_refundable_ctc_total_household_income", period
        )
        return total_household_income <= income_limit
