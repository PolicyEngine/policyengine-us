from policyengine_us.model_api import *


class ut_hb210_s2_marriage_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Utah HB 210 Substitute 2 marriage tax credit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.UT
    reference = (
        "https://le.utah.gov/~2026/bills/static/HB0210.html",
        "Utah Code Section 59-10-1049",
    )
    documentation = """
    Utah HB 210 Substitute 2 creates a standalone nonrefundable marriage tax credit.

    Eligibility:
    - Filing status must be joint, surviving spouse, or married filing separately
    - MAGI must not exceed the applicable income limit (hard cutoff, no phaseout)

    Amount:
    - $158 for joint and surviving spouse filers
    - $79 for married filing separately

    The credit is nonrefundable (cannot exceed state income tax liability).

    MAGI per 59-10-1047: AGI + interest income not in AGI + Section 59-10-114 additions.
    For simplicity, this implementation uses AGI as a proxy for MAGI.
    """

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.contrib.states.ut.hb210.s2_marriage_credit

        filing_status = tax_unit("filing_status", period)

        # Get credit amount by filing status (0 for ineligible statuses)
        credit_amount = p.amount[filing_status]

        # Get income limit by filing status
        income_limit = p.income_limit[filing_status]

        # Use AGI as proxy for MAGI
        # Full MAGI = AGI + interest not in AGI + 59-10-114 additions
        agi = tax_unit("adjusted_gross_income", period)

        # Check income eligibility (hard cutoff)
        income_eligible = agi <= income_limit

        # Credit is only available to eligible filers under income limit
        eligible_credit = where(income_eligible, credit_amount, 0)

        # Credit is nonrefundable - cap at tax liability
        tax_before_credits = tax_unit(
            "ut_income_tax_before_non_refundable_credits", period
        )

        return min_(eligible_credit, tax_before_credits)
