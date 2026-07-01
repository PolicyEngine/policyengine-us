from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.wi.tax.income.wi_standard_deduction import (
    wi_standard_deduction_for_income,
)


class wi_retirement_income_exclusion_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Wisconsin retirement income exclusion path tax"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://docs.legis.wisconsin.gov/statutes/statutes/71/i/05/6/b/54m/a",
        "https://www.revenue.wi.gov/TaxForms2025/2025-ScheduleSB-Inst.pdf#page=7",
    )
    defined_for = StateCode.WI

    def formula(tax_unit, period, parameters):
        # Schedule SB Line 16 path: tax on income reduced by the
        # exclusion amount, with zero credits applied.
        # wi_taxable_income already includes Line 17; per the Line 17
        # worksheet (step 4), Line 17 self-adjusts downward when
        # Line 16 is claimed, so we simply subtract Line 16 here.
        line16 = tax_unit("wi_retirement_income_exclusion_amount", period)
        taxinc = tax_unit("wi_taxable_income", period)

        # The Line 16 subtraction reduces WI income (Form 1 line 7), and the
        # standard deduction (line 8) is looked up on that post-subtraction
        # income. wi_taxable_income embeds the standard deduction computed on
        # the higher pre-subtraction income, so add back the extra standard
        # deduction the subtraction unlocks. This is algebraically equivalent
        # to recomputing taxable income on the reduced WI income, and keeps
        # the phaseout from staying keyed to the pre-subtraction income.
        fstatus = tax_unit("filing_status", period)
        wi_agi = tax_unit("wi_agi", period)
        standard_deduction_full = tax_unit("wi_standard_deduction", period)
        standard_deduction_reduced = wi_standard_deduction_for_income(
            max_(0, wi_agi - line16), fstatus, parameters, period
        )
        extra_standard_deduction = standard_deduction_reduced - standard_deduction_full
        exclusion_taxinc = max_(0, taxinc - line16 - extra_standard_deduction)

        statuses = fstatus.possible_values
        p = parameters(period).gov.states.wi.tax.income
        return select(
            [
                fstatus == statuses.SINGLE,
                fstatus == statuses.JOINT,
                fstatus == statuses.SURVIVING_SPOUSE,
                fstatus == statuses.SEPARATE,
                fstatus == statuses.HEAD_OF_HOUSEHOLD,
            ],
            [
                p.rates.single.calc(exclusion_taxinc),
                p.rates.joint.calc(exclusion_taxinc),
                p.rates.joint.calc(exclusion_taxinc),
                p.rates.separate.calc(exclusion_taxinc),
                p.rates.head_of_household.calc(exclusion_taxinc),
            ],
        )
