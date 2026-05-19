from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.tax.income.non_refundable_credit_cap import (
    state_non_refundable_credit_limit,
)


class ok_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Oklahoma EITC"
    unit = USD
    definition_period = YEAR
    reference = (
        # 2025 Form 511-EIC instructions
        "https://oklahoma.gov/content/dam/ok/en/tax/documents/forms/individuals/current/511-EIC.pdf",
        # Oklahoma Statutes 68 O.S. Section 2357.43 - Earned Income Tax Credit
        "https://law.justia.com/codes/oklahoma/title-68/section-68-2357-43/",
        # HB 2962 (Laws 2021, c. 493) enrolled - restored refundability from 2022
        "https://www.oklegislature.gov/cf_pdf/2021-22%20ENR/hB/HB2962%20ENR.PDF",
    )
    defined_for = StateCode.OK
    documentation = """
    Oklahoma Earned Income Tax Credit (EITC).

    Oklahoma provides a state EITC equal to 5% of the federal EITC amount,
    but uses FROZEN 2020 federal EITC parameters rather than current year
    parameters. This is a unique feature of Oklahoma's EITC.

    Per 68 O.S. Section 2357.43: The Oklahoma credit is calculated using
    the federal EITC parameters that were in effect for tax year 2020,
    regardless of the current tax year.

    Refundability history:
    - 2002-2015: Refundable (original enactment, Laws 2001, c. 383)
    - 2016-2021: Non-refundable (Laws 2016, c. 341 sec. 1)
    - 2022-present: Refundable (HB 2962, Laws 2021, c. 493 sec. 2)

    When the credit is listed as non-refundable for the period, the
    tentative amount is capped at the remaining Oklahoma tax liability
    after credits that appear earlier in the nonrefundable ordering.
    """

    def formula(tax_unit, period, parameters):
        us_agi = tax_unit("adjusted_gross_income", period)
        ok_agi = tax_unit("ok_agi", period)
        agi_ratio = np.zeros_like(us_agi)
        mask = us_agi != 0
        agi_ratio[mask] = ok_agi[mask] / us_agi[mask]
        prorate = min_(1, max_(0, agi_ratio))
        federal_eitc = tax_unit("ok_federal_eitc", period)
        p = parameters(period).gov.states.ok.tax.income.credits
        tentative = prorate * p.earned_income.eitc_fraction * federal_eitc
        # Laws 2016, c. 341 made the credit non-refundable; HB 2962 (Laws
        # 2021, c. 493) restored refundability effective 2022-01-01. When
        # non-refundable, cap at the remaining liability after credits
        # preceding ok_eitc in the ordered nonrefundable list.
        if "ok_eitc" in p.nonrefundable:
            remaining_tax = state_non_refundable_credit_limit(
                tax_unit,
                period,
                p.nonrefundable,
                "ok_income_tax_before_credits",
                "ok_eitc",
            )
            return min_(tentative, remaining_tax)
        return tentative
