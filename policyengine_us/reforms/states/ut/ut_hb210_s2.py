from policyengine_us.model_api import *
from policyengine_core.periods import period as period_
from policyengine_core.periods import instant


def create_ut_hb210_s2() -> Reform:
    """
    Utah HB 210 Substitute 2 - Marriage tax credit (Section 59-10-1049)

    Creates a standalone nonrefundable marriage tax credit:
    - $158 for joint and surviving spouse filers
    - $79 for married filing separately
    - MAGI income limits: $90,000 (joint/surviving), $45,000 (separate)
    - Hard cutoff, no phaseout

    This is separate from the taxpayer credit add-on in the original bill
    and Substitute 1 (implemented in ut_hb210.py).
    """

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
            p = parameters(
                period
            ).gov.contrib.states.ut.hb210.s2_marriage_credit

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

    def modify_parameters(parameters):
        # Add ut_hb210_s2_marriage_credit to non-refundable credits list
        non_refundable = (
            parameters.gov.states.ut.tax.income.credits.non_refundable
        )
        current_credits = non_refundable(instant("2026-01-01"))
        if "ut_hb210_s2_marriage_credit" not in current_credits:
            new_credits = list(current_credits) + [
                "ut_hb210_s2_marriage_credit"
            ]
            non_refundable.update(
                start=instant("2026-01-01"),
                stop=instant("2100-12-31"),
                value=new_credits,
            )
        return parameters

    class reform(Reform):
        def apply(self):
            self.modify_parameters(modify_parameters)
            self.add_variable(ut_hb210_s2_marriage_credit)

    return reform


def create_ut_hb210_s2_reform(parameters, period, bypass: bool = False):
    if bypass:
        return create_ut_hb210_s2()

    p = parameters.gov.contrib.states.ut.hb210.s2_marriage_credit

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_ut_hb210_s2()
    else:
        return None


ut_hb210_s2 = create_ut_hb210_s2_reform(None, None, bypass=True)
