from policyengine_us.model_api import *


class casualty_loss_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Casualty loss deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/165#h",
        # 2017 Form 4684, lines 10-18
        "https://www.irs.gov/pub/irs-prior/f4684--2017.pdf#page=1",
        # IRS Publication 547 (2017), $100 Rule
        "https://www.irs.gov/pub/irs-prior/p547--2017.pdf#page=10",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.irs.deductions.itemized.casualty
        # Only the owner of the property claims the loss. A dependent's loss
        # belongs on the dependent's own return, as the dependent's income
        # does: adjusted gross income leaves it out.
        loss = tax_unit_non_dep_add(tax_unit, period, ["casualty_loss"])
        # 26 U.S.C. 165(h)(1) reduces each casualty by $100 (Form 4684
        # line 11). A joint return is one individual for the $100 rule
        # (165(h)(4)(B)). The model records one loss amount per person, not
        # separate casualty events, so the return's losses are treated as one
        # casualty and the reduction applies once.
        reduced_loss = max_(loss - p.per_casualty_reduction, 0)
        # 165(h)(2)(A): the rest is allowed above 10% of adjusted gross income
        # (Form 4684 line 17).
        positive_agi = tax_unit("positive_agi", period)
        amount_over_floor = max_(reduced_loss - positive_agi * p.floor, 0)
        return p.active * amount_over_floor
