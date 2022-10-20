from policyengine_us.model_api import *
import numpy as np


class md_standard_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD standard deduction"
    unit = USD
    definition_period = YEAR
    reference = "https://govt.westlaw.com/mdc/Document/NC8EB19606F6911E8A99BCF2C90B83D38?viewType=FullText&originationContext=documenttoc&transitionType=CategoryPageItem&contextData=(sc.Default)#co_anchor_I552E3B107DF711ECA8F2FF3A9E62BB69"
    defined_for = StateCode.MD

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        p = parameters(period).gov.states.md.tax.income.deductions.standard
        md_agi = tax_unit("md_agi", period)
        # Standard deduction is a percentage of AGI, bounded by a min/max by filing status.
        return np.clip(
            p.rate * md_agi, p.min[filing_status], p.max[filing_status]
        )
