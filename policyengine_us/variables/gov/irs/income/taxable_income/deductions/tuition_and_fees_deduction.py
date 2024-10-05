from policyengine_us.model_api import *


class tuition_and_fees_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Tuition and fees deduction"
    unit = USD
    defined_for = "tuition_and_fees_deduction_eligible"
    definition_period = YEAR
    reference = (
        "https://www.irs.gov/pub/irs-pdf/f8917.pdf#page=2"
        # Law was repealed in 2021
        "https://irc.bloombergtax.com/public/uscode/doc/irc/section_222"
    )

    def formula(tax_unit, period, parameters):
        qualified_tuition_expenses = add(
            tax_unit, period, ["qualified_tuition_expenses"]
        )
        adjusted_gross_income = tax_unit("adjusted_gross_income", period)
        p = parameters(period).gov.irs.deductions.tuition_and_fees
        filing_status = tax_unit("filing_status", period)
        joint = filing_status == filing_status.possible_values.JOINT
        cap = where(
            joint,
            p.joint.calc(adjusted_gross_income),
            p.non_joint.calc(adjusted_gross_income),
        )
        return min_(qualified_tuition_expenses, cap)
