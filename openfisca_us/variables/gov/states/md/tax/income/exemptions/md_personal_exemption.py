from openfisca_us.model_api import *


class md_personal_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD value per personal exemption"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        # Get filing status and AGI.
        filing_status = tax_unit("filing_status", period)
        filing_statuses = filing_status.possible_values
        agi = tax_unit("adjusted_gross_income", period)
        # Calculate for single and separate depending on AGI.
        p = parameters(period).gov.states.md.tax.income.exemptions.personal
        single_separate = p.single_separate.calc(agi, right=True)
        # Calculate for joint, head of household, and widow based on AGI.
        joint_head_widow = p.joint_head_widow.calc(agi, right=True)
        # Return the value matching filing status.
        is_single_separate = (filing_status == filing_statuses.SINGLE) | (
            filing_status == filing_statuses.SEPARATE
        )
        return where(is_single_separate, single_separate, joint_head_widow)
