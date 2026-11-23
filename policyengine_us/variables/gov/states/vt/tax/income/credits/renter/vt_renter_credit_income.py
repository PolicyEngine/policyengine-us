from policyengine_us.model_api import *


class vt_renter_credit_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Vermont renter credit income"
    unit = USD
    documentation = (
        "Income for the Vermont renter credit under 32 V.S.A. 6061(18): "
        "federal adjusted gross income plus the business, rental, farm and "
        "capital losses it deducted, tax-exempt interest, 75 percent of the "
        "claimant's and spouse's nontaxable Social Security, and the listed "
        "above-the-line deductions."
    )
    definition_period = YEAR
    reference = (
        "https://legislature.vermont.gov/statutes/section/32/154/06061",  # (18)
        "https://law.justia.com/codes/vermont/2022/title-32/chapter-154/section-6061/",  # (18)
        "https://tax.vermont.gov/sites/tax/files/documents/RCC-146-2025.pdf#page=1",  # lines 10-14
        "https://tax.vermont.gov/sites/tax/files/documents/Income-Booklet-2025.pdf#page=39",  # lines 10-14
        "https://tax.vermont.gov/sites/tax/files/documents/Income%20Booklet-2022.pdf#page=36",
    )
    defined_for = StateCode.VT

    adds = [
        "adjusted_gross_income",
        # (18)(A): the losses federal adjusted gross income deducted. Each
        # head's and spouse's loss in each category (sole proprietorship,
        # farm, rental, farm rental, partnership or S corporation, estate or
        # trust, and sale of business property) is added back, because the
        # statute lists each kind of loss. RCC-146 line 13 adds back a
        # negative Schedule 1 line 3, 4, 5 or 6, after the items on that line
        # net, so a loss offset by other income on the same line adds nothing
        # there.
        "limited_business_loss",
        # (18)(A) "capital loss": each loss from a sale or exchange
        # (26 U.S.C. 1222(2), (4)) that adjusted gross income deducted,
        # including a loss netted against the same person's gains. RCC-146
        # line 13 adds back only the net loss on Form 1040 line 7.
        "vt_renter_credit_capital_loss_add_back",
        # (18)(B); RCC-146 line 12.
        "tax_exempt_interest_income",
        # (18)(C); RCC-146 line 11.
        "vt_renter_credit_countable_tax_exempt_ss",
        # (18)(D).
        "vt_renter_credit_deduction_add_back",
    ]
