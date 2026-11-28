from policyengine_us.model_api import *


class mn_renters_credit_household_agi(Variable):
    value_type = float
    entity = TaxUnit
    label = "Minnesota renter's credit household adjusted gross income"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Adjusted gross income of the claimant and spouse, Schedule M1RENT "
        "lines 1 to 3. The household is the claimant and the claimant's "
        "spouse (Minn. Stat. 290.0693, subd. 1(g), and 290A.03, subd. 4), so "
        "other adults in the home, such as roommates, claim with their own "
        "income (290.0693, subd. 7)."
    )
    reference = (
        "https://www.revisor.mn.gov/statutes/cite/290.0693",
        "https://www.revisor.mn.gov/statutes/cite/290A.03",
        # PDF pages 3-4: the filing situations table ("Lived with a roommate
        # ... Include only your income when filing for the credit") and the
        # line 1 and line 2 instructions.
        "https://www.revenue.state.mn.us/sites/default/files/2026-07/m1rent-25.pdf#page=3",
    )
    defined_for = StateCode.MN

    def formula(tax_unit, period, parameters):
        # Line 1 is the filer's federal AGI, which leaves out tax unit
        # dependents' income, as household income does (subd. 1(h)). Line 2
        # adds a separate filer's spouse's AGI.
        filing_status = tax_unit("filing_status", period)
        separate = filing_status == filing_status.possible_values.SEPARATE
        return tax_unit("adjusted_gross_income", period) + (
            tax_unit("spouse_separate_adjusted_gross_income", period) * separate
        )
