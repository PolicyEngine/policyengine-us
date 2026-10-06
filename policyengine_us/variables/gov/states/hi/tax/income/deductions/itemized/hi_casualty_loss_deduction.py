from policyengine_us.model_api import *


class hi_casualty_loss_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii casualty loss deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        # HRS § 235-2.4(l)
        "https://files.hawaii.gov/tax/legal/hrs/hrs_235.pdf#page=12",
        # 2022 Form N-11 instructions, Casualty and Theft Losses and
        # Worksheet A-5
        "https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=18",
        "https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=32",
        # 2025 Form N-11 instructions, Casualty and Theft Losses and
        # Worksheet A-5
        "https://files.hawaii.gov/tax/forms/2025/n11ins.pdf#page=19",
        "https://files.hawaii.gov/tax/forms/2025/n11ins.pdf#page=34",
        # 2017 Form 4684, lines 10-16
        "https://www.irs.gov/pub/irs-prior/f4684--2017.pdf#page=1",
        # Department of Taxation Announcement 2026-06: Act 35, SLH 2026,
        # conforms to 26 U.S.C. 165(h)(5) from 2026
        "https://files.hawaii.gov/tax/news/announce/ann26-06.pdf#page=2",
    )
    defined_for = StateCode.HI

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.hi.tax.income.deductions.itemized
        p_irs = parameters(period).gov.irs.deductions.itemized.casualty
        # Worksheet A-5 line 19 takes the loss from the 2017 federal Form 4684,
        # line 16: each casualty less Hawaii's $100 (HRS 235-2.4(l)(1)).
        # Hawaii did not adopt the federal qualified-disaster rules, which
        # replace the $100 with $500 and waive the 10% floor.
        # Only the owner of the property claims the loss. A dependent's loss
        # belongs on the dependent's own return.
        loss = tax_unit_non_dep_add(tax_unit, period, ["casualty_loss"])
        # A joint return is one individual for the $100 rule. The model records
        # one loss amount per person, not separate casualty events, so the
        # return's losses are treated as one casualty and the reduction
        # applies once.
        reduced_loss = max_(loss - p.casualty_loss.per_casualty_reduction, 0)
        # Lines 20-22: less 10% of Hawaii adjusted gross income, floored at
        # zero.
        hi_agi = tax_unit("hi_agi", period)
        floor = max_(0, p_irs.floor * hi_agi)
        deduction = max_(reduced_loss - floor, 0)
        # Through 2025 Hawaii did not limit personal casualty losses to
        # declared disasters (HRS 235-2.4(l)(3) made 26 U.S.C. 165(h)(5)
        # inoperative). Act 35, SLH 2026, adopts that limit from 2026. The
        # model has no input that distinguishes disaster losses, so, like the
        # federal deduction, no personal casualty loss is deductible once the
        # limit applies.
        return p.casualty_loss.non_disaster_losses_allowed * deduction
