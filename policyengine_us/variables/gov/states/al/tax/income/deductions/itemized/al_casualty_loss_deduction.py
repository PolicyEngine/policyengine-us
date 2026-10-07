from policyengine_us.model_api import *


class al_casualty_loss_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Alabama casualty loss deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        # Ala. Code § 40-18-15(a)(6)
        "https://alison.legislature.state.al.us/code-of-alabama?section=40-18-15",
        # Ala. Code § 40-18-1.1(b): "26 U.S.C." means the Internal Revenue
        # Code as in effect from time to time
        "https://alison.legislature.state.al.us/code-of-alabama?section=40-18-1.1",
        # 2025 Form 40 instructions, Schedule A lines 19a-c, and Schedule A
        "https://www.revenue.alabama.gov/wp-content/uploads/2026/01/25f40bk.pdf#page=20",
        "https://www.revenue.alabama.gov/wp-content/uploads/2026/01/25f40schabdc_blk.pdf#page=1",
        # 2021 Form 40 instructions, Schedule A lines 19a-c
        "https://www.revenue.alabama.gov/wp-content/uploads/2022/06/21f40bk.pdf#page=20",
        # 2025 Form 4684, lines 10-16
        "https://www.irs.gov/pub/irs-prior/f4684--2025.pdf#page=1",
        # Alabama Department of Revenue, OBBBA Executive Summary: 26 U.S.C.
        # 165(h)(5) is "Tied to Federal: Yes" through 40-18-15(a)(6)
        "https://www.revenue.alabama.gov/wp-content/uploads/2025/11/OBBBA-Executive-Summary_FinalwAppendixA_10.31.25.pdf#page=8",
    )
    defined_for = StateCode.AL

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.irs.deductions.itemized.casualty
        # Alabama allows the loss as determined under 26 U.S.C. 165(c)(3) and
        # (h), as in effect from time to time. Schedule A line 19a takes the
        # loss from federal Form 4684, after each casualty is reduced by $100
        # (line 11) and, from 2018, after the limit to losses attributable to
        # declared disasters (165(h)(5), line 14). The Department of Revenue
        # ties Alabama to 165(h)(5) explicitly for tax years after 2025; for
        # 2018-2025 the limit follows from the rolling conformity and the form
        # flow. The model has no input that distinguishes disaster losses, so,
        # like the federal deduction, no personal casualty loss is deductible
        # while gov.irs.deductions.itemized.casualty.active is false (from
        # 2018).
        # Only the owner of the property claims the loss. A dependent's loss
        # belongs on the dependent's own return.
        loss = tax_unit_non_dep_add(tax_unit, period, ["casualty_loss"])
        # A joint return is one individual for the $100 rule. The model records
        # one loss amount per person, not separate casualty events, so the
        # return's losses are treated as one casualty and the reduction
        # applies once.
        reduced_loss = max_(loss - p.per_casualty_reduction, 0)
        # Line 19b: 10% of Alabama adjusted gross income (Form 40, line 10).
        # The form is silent on a negative AGI; like the federal deduction
        # (positive_agi) and Hawaii's Worksheet A-5, the floor is not allowed
        # to go below zero, so the deduction never exceeds the reduced loss.
        al_agi = max_(tax_unit("al_agi", period), 0)
        return p.active * max_(reduced_loss - al_agi * p.floor, 0)
