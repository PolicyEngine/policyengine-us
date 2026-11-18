from policyengine_us.model_api import *


class co_alternative_minimum_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Colorado alternative minimum taxable income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CO
    reference = [
        "https://tax.colorado.gov/DR0104AMT",
        "https://law.justia.com/codes/colorado/2022/title-39/article-22/part-1/section-39-22-105/",
        # C.R.S. 39-22-104(3)(d)(I), 39-22-104(4)(e) and 39-22-105(2)(a),
        # Colorado Revised Statutes 2025. PDF pages 380, 386, 401
        "https://olls.info/crs/crs2025-title-39.pdf#page=380",
        # 2025 DR 0104AMT instructions and computation schedule
        # PDF pages 1, 3
        "https://tax.colorado.gov/sites/tax/files/documents/DR0104AMT_2025.pdf#page=1",
        # 2025 DR 0104 lines 2 through 9
        "https://tax.colorado.gov/sites/tax/files/documents/DR0104_2025.pdf#page=3",
    ]

    def formula(tax_unit, period, parameters):
        # C.R.S. 39-22-105(2)(a) applies the 39-22-104 modifications to
        # federal alternative minimum taxable income less the exemption.
        # Measured against that base, the state income tax addback of
        # 39-22-104(3)(d) ("an amount equal to the deduction claimed") is
        # zero, since 26 U.S.C. 56(b)(1)(A)(ii) allows no such deduction, and
        # the refund subtraction of 39-22-104(4)(e), whose stated purpose is
        # "to avoid re-taxing" the refund, has nothing to offset, since 26
        # U.S.C. 56(b)(1)(C) already leaves the refund out. DR 0104AMT lines
        # 2 and 4 leave out both.
        # Line 1: Form 6251 line 6, or, when the exemption (line 5) exceeds
        # alternative minimum taxable income (line 4) and line 6 is zero,
        # line 4 less line 5 as a negative amount.
        line_6 = tax_unit("amt_income_less_exemptions", period)
        shortfall = min_(
            0, tax_unit("amt_income", period) - tax_unit("amt_exemption", period)
        )
        line_1 = where(line_6 > 0, line_6, shortfall)
        # Line 2: Colorado additions from DR 0104, lines 3 through 7 and 9,
        # leaving out the state income tax addback on DR 0104 line 2.
        line_2 = tax_unit("co_additions", period) - tax_unit("co_state_addback", period)
        # Line 4: the DR 0104AD subtractions excluding the state income tax
        # refund (DR 0104AD line 1). co_subtractions is floored at zero, and
        # so is this line, so the refund can never act as an addition.
        line_4 = max_(
            0,
            tax_unit("co_subtractions", period)
            - add(tax_unit, period, ["salt_refund_income"]),
        )
        # Line 5: Colorado alternative minimum taxable income.
        return max_(0, line_1 + line_2 - line_4)
