from openfisca_us.model_api import *


class amt_income(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "AMT taxable income"
    unit = USD
    reference = "https://www.law.cornell.edu/uscode/text/26/55#b_2"

    def formula(tax_unit, period, parameters):
        taxable_income = tax_unit("taxable_income", period)
        # Add back excluded deductions
        itemizing = tax_unit("tax_unit_itemizes", period)
        standard_deduction = tax_unit("standard_deduction", period)
        salt_deduction = tax_unit("salt_deduction", period)
        excluded_deductions = where(
            itemizing,
            salt_deduction,
            standard_deduction,
        )
        amt_income = taxable_income + excluded_deductions
        amt = parameters(period).gov.irs.income.amt
        filing_status = tax_unit("filing_status", period)
        separate_addition = max_(
            0,
            min_(
                amt.exemption.amount[filing_status],
                amt.exemption.phase_out.rate
                * max_(0, amt_income - amt.exemption.separate_limit),
            ),
        ) * (filing_status == filing_status.possible_values.SEPARATE)
        return amt_income + separate_addition
