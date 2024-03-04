from policyengine_us.model_api import *


class tuition_and_fees_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Tuition and fees deduction"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        qualified_tuition_expenses = add(
            tax_unit, period, ["qualified_tuition_expenses"]
        )
        adjusted_gross_income = tax_unit("adjusted_gross_income", period)
        filing_status = tax_unit("filing_status", period)
        p = parameters(period).gov.irs.deductions.tuition_and_fees
        limit = select(
            [
                filing_status == filing_status.possible_values.JOINT,
                filing_status != filing_status.possible_values.JOINT,
            ],
            [
                p.joint.calc(adjusted_gross_income),
                p.non_joint.calc(adjusted_gross_income),
            ],
        )
        return min_(qualified_tuition_expenses, limit)
