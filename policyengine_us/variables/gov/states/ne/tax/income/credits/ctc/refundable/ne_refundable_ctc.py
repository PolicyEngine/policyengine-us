from policyengine_us.model_api import *


class ne_refundable_ctc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Nebraska refundable Child Tax Credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://nebraskalegislature.gov/laws/statutes.php?statute=77-7203"
    )
    defined_for = StateCode.NE

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ne.tax.income.credits.ctc.refundable
        # Total household income is defined as federal adjusted gross income
        # as per Nebraska Department of Revenue
        adjusted_gross_income = tax_unit("adjusted_gross_income", period)
        credit_amount = p.amount.calc(adjusted_gross_income)
        qualifying_children = add(
            tax_unit, period, ["ne_refundable_ctc_eligible_child"]
        )
        return credit_amount * qualifying_children
