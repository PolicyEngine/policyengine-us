from openfisca_us.model_api import *
from openfisca_us.variables.gov.irs.income.taxable_income.deductions.standard_deduction.standard_deduction import (
    standard_deduction,
)


class md_standard_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD standard deduction"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        filing_statuses = filing_status.possible_values
        p = parameters(period).gov.states.md.tax.income.standard_deduction
        # Start with md_agi
        md_agi = tax_unit("md_agi", period)

        # Caculate for single and separate depending on AGI.
        single_separate = max_(
            min_(
                p.rate * md_agi,
                p.single_separate.max,
            ),
            p.single_separate.min,
        )
        # Calculate for joint, head of household, and widow based on AGI.
        joint_head_widow = max_(
            min_(
                p.rate * md_agi,
                p.joint_head_widow.max,
            ),
            p.joint_head_widow.min,
        )
        # Return the value matching filing status.
        return where(
            (filing_status == filing_statuses.SINGLE)
            | (filing_status == filing_statuses.SEPARATE),
            single_separate,
            joint_head_widow,
        )
