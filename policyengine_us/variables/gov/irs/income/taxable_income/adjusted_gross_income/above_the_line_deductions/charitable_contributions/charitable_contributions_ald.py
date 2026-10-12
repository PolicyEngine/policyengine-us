from policyengine_us.model_api import *


class charitable_contributions_ald(Variable):
    value_type = float
    entity = TaxUnit
    label = "Above-the-line charitable deduction for non-itemizers"
    unit = USD
    documentation = (
        "Above-the-line deduction for cash charitable contributions by a tax "
        "unit that does not itemize (26 U.S.C. 62(a)(22), 2020 Form 1040 line "
        "10b), which reduces adjusted gross income. It applies to taxable "
        "years beginning in 2020 only; the 2021 and later deductions for "
        "non-itemizers (26 U.S.C. 170(p)) are taken from adjusted gross "
        "income in charitable_deduction_for_non_itemizers. Cash donations "
        "are not split by recipient, so contributions to supporting "
        "organizations and donor advised funds, which 62(f)(2) excludes, "
        "are counted."
    )
    definition_period = YEAR
    reference = (
        # CARES Act sec. 2204: 26 U.S.C. 62(a)(22) and 62(f).
        "https://www.congress.gov/116/plaws/publ136/PLAW-116publ136.pdf#page=65",
        # 2020 Instructions for Form 1040, line 10b.
        "https://www.irs.gov/pub/irs-prior/i1040gi--2020.pdf#page=30",
    )

    def formula(tax_unit, period, parameters):
        # Only in years that list it among above-the-line deductions, where
        # tax_unit_itemizes takes the itemization choice from branches.
        # State additions that read it then never reach the choice in other
        # years.
        if (
            "charitable_contributions_ald"
            not in parameters(period).gov.irs.ald.deductions
        ):
            return 0
        p = parameters(period).gov.irs.ald.charitable_contributions
        # 62(f)(1): an eligible individual is one who does not elect to
        # itemize deductions.
        itemizes = tax_unit("tax_unit_itemizes", period)
        cash_donations = add(tax_unit, period, ["charitable_cash_donations"])
        filing_status = tax_unit("filing_status", period)
        return ~itemizes * min_(cash_donations, p.cap[filing_status])
