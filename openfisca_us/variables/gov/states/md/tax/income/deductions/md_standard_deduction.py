from openfisca_us.model_api import *
import numpy as np


class md_standard_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD standard deduction"
    unit = USD
    definition_period = YEAR
    reference = "https://govt.westlaw.com/mdc/Document/NC8EB19606F6911E8A99BCF2C90B83D38?viewType=FullText&originationContext=documenttoc&transitionType=CategoryPageItem&contextData=(sc.Default)#co_anchor_I552E3B107DF711ECA8F2FF3A9E62BB69"

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        filing_statuses = filing_status.possible_values
        p = parameters(period).gov.states.md.tax.income.deductions.standard
        md_agi = tax_unit("md_agi", period)
        # Standard deduction is a percentage of AGI, bounded by a min/max by filing status.
        # Calculate for single and separate depending on AGI.
        single_separate = np.clip(
            p.rate * md_agi, p.single_separate.min, p.single_separate.max
        )
        # Calculate for joint, head of household, and widow based on AGI.
        joint_head_widow = np.clip(
            p.rate * md_agi, p.joint_head_widow.min, p.joint_head_widow.max
        )
        # Return the value matching filing status.
        is_single_separate = (filing_status == filing_statuses.SINGLE) | (
            filing_status == filing_statuses.SEPARATE
        )
        return where(is_single_separate, single_separate, joint_head_widow)
