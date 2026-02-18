from policyengine_us.model_api import *


class wi_retirement_income_exclusion_tax_reduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Wisconsin retirement income exclusion tax reduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://docs.legis.wisconsin.gov/statutes/statutes/71/i/05/6/b/54m/a",
        "https://www.revenue.wi.gov/TaxForms2025/2025-ScheduleSB-Inst.pdf#page=7",
    )
    defined_for = "wi_retirement_income_exclusion_eligible"

    def formula(tax_unit, period, parameters):
        # Schedule SB instructions p.7: compare tax under two paths.
        # Claiming Line 16 forfeits ALL credits (Schedule CR, Form 1
        # lines 13-20 and 30-35), so the taxpayer picks the lower tax.
        #
        # Path A (standard): tax after all credits (Line 17 subtraction
        #   already in wi_taxable_income).
        # Path B (exclusion): recompute tax on (taxinc - Line 16 +
        #   Line 17), with zero credits.
        # Reduction = max(0, Path A tax - Path B tax).

        # Path A: standard tax
        standard_tax = tax_unit(
            "wi_income_tax_before_refundable_credits", period
        ) - tax_unit("wi_refundable_credits", period)

        # Path B: exclusion tax (Line 16, no credits)
        line16 = tax_unit("wi_retirement_income_exclusion_amount", period)
        line17 = tax_unit("wi_retirement_income_subtraction", period)
        taxinc = tax_unit("wi_taxable_income", period)
        # Add Line 17 back because wi_taxable_income already subtracted it
        exclusion_taxinc = max_(0, taxinc - line16 + line17)

        fstatus = tax_unit("filing_status", period)
        statuses = fstatus.possible_values
        p = parameters(period).gov.states.wi.tax.income
        exclusion_tax = select(
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

        return max_(0, standard_tax - exclusion_tax)
