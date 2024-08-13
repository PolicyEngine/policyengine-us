from policyengine_us.model_api import *


class ne_refundable_ctc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Nebraska refundable Child Tax Credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://nebraskalegislature.gov/laws/statutes.php?statute=77-7203",
        "https://revenue.nebraska.gov/businesses/child-care-tax-credit-act",
    )
    defined_for = StateCode.NE

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ne.tax.income.credits.ctc.refundable
        total_household_income = tax_unit(
            "ne_refundable_ctc_total_household_income", period
        )
        credit_amount = p.amount.calc(total_household_income)
        qualifying_children = add(
            tax_unit, period, ["ne_refundable_ctc_eligible_child"]
        )
        return credit_amount * qualifying_children
