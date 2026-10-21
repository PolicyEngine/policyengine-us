from policyengine_us.model_api import *


class md_standard_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD standard deduction"
    unit = USD
    definition_period = YEAR
    reference = [
        "https://mgaleg.maryland.gov/2024RS/Statute_Web/gtg/10-217.pdf",
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
        return np.clip(p.rate * md_agi, p.min[filing_status], p.max[filing_status])
