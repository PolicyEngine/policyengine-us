from policyengine_us.model_api import *


class md_standard_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD standard deduction"
    unit = USD
    definition_period = YEAR
    reference = [
        "https://govt.westlaw.com/mdc/Document/NC8EB19606F6911E8A99BCF2C90B83D38?viewType=FullText&originationContext=documenttoc&transitionType=CategoryPageItem&contextData=(sc.Default)#co_anchor_I552E3B107DF711ECA8F2FF3A9E62BB69",
        "https://mgaleg.maryland.gov/2025RS/Chapters_noln/CH_604_hb0352e.pdf#page=165",  # Maryland House Bill 352 - Budget Reconciliation and Financing Act of 2025
    ]
    defined_for = StateCode.MD

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        p = parameters(period).gov.states.md.tax.income.deductions.standard

        # Use flat amounts when applicable
        if p.flat_deduction.applies:
            return p.flat_deduction.amount[filing_status]

        # For years when flat deduction doesn't apply, use the old formula:
        # standard deduction is a percentage of AGI that
        # is bounded by a min/max by filing status.
        md_agi = tax_unit("md_agi", period)
        return np.clip(
            p.rate * md_agi, p.min[filing_status], p.max[filing_status]
        )
