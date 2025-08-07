from policyengine_us.model_api import *


class amt_separate_addition(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "AMT taxable income separate addition"
    unit = USD
    reference = "https://www.law.cornell.edu/uscode/text/26/55#b_2"

    def formula(tax_unit, period, parameters):
        taxable_income = tax_unit("taxable_income", period)
        excluded_deductions = tax_unit("amt_excluded_deductions", period)
        amt_inc = taxable_income + excluded_deductions
        p = parameters(period).gov.irs.income.amt.exemption
        filing_status = tax_unit("filing_status", period)
        separate = filing_status == filing_status.possible_values.SEPARATE
        reduced_amt_inc = max_(0, amt_inc - p.separate_limit)
        return (
            max_(
                0,
                min_(
                    p.amount[filing_status],
                    p.phase_out.rate * reduced_amt_inc,
                ),
            )
            * separate
        )
