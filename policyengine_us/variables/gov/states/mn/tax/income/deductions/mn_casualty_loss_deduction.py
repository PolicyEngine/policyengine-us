from policyengine_us.model_api import *


class mn_casualty_loss_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Minnesota casualty loss deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        # Minn. Stat. § 290.0122, subd. 8: losses under 26 U.S.C. 165(c)(3),
        # including 165(h) but disregarding (h)(5)
        "https://www.revisor.mn.gov/statutes/cite/290.0122#stat.290.0122.8",
        # 2024 Schedule M1SA, line 19, and its instructions
        # PDF pages 1, 7
        "https://www.revenue.state.mn.us/sites/default/files/2024-12/m1sa-24.pdf#page=1",
        # 2024 Schedule M1CAT, lines 10-20
        "https://www.revenue.state.mn.us/sites/default/files/2024-12/m1cat-24.pdf#page=1",
        # 2018 Schedule M1CAT, lines 10-20
        "https://www.revenue.state.mn.us/sites/default/files/2018-11/m1cat_18.pdf#page=1",
    )
    defined_for = StateCode.MN
    documentation = """
    Minnesota allows personal casualty and theft losses under 26 U.S.C. 165(h)
    but disregards the federal limit to declared disasters (Minn. Stat.
    290.0122, subd. 8). Schedule M1CAT reduces each casualty by $100 and allows
    the rest above 10% of Form M1 line 1 (federal adjusted gross income); the
    result goes on Schedule M1SA line 19.
    """

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.irs.deductions.itemized.casualty
        # For 2018 Minnesota computed tax under the Internal Revenue Code as
        # amended through December 16, 2016 (Minn. Stat. 290.993), before
        # 26 U.S.C. 165(h)(5) existed, and Schedule M1CAT has applied the same
        # $100 and 10% computation in every year since, so the federal
        # suspension never applies.
        # Only the owner of the property claims the loss. A dependent's loss
        # belongs on the dependent's own return, as the dependent's income
        # does: adjusted gross income leaves it out.
        loss = tax_unit_non_dep_add(tax_unit, period, ["casualty_loss"])
        # M1CAT line 11: "Enter $100". A joint return is one individual for the
        # $100 rule (165(h)(4)(B)). The model records one loss amount per
        # person, not separate casualty events, so the return's losses are
        # treated as one casualty and the reduction applies once.
        reduced_loss = max_(loss - p.per_casualty_reduction, 0)
        # M1CAT lines 18-20: subtract 10% of Form M1 line 1 (federal adjusted
        # gross income). The form does not say to enter 0 for a negative
        # AGI; like Form 4684 and the federal deduction, the floor is not
        # allowed to go below zero, so the deduction never exceeds the
        # reduced loss.
        positive_agi = tax_unit("positive_agi", period)
        return max_(reduced_loss - positive_agi * p.floor, 0)
