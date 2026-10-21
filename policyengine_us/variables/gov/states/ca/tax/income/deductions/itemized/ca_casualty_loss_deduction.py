from policyengine_us.model_api import *


class ca_casualty_loss_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "California casualty loss deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        # Cal. Rev. & Tax. Code § 17201: the IRC itemized deductions,
        # including 26 U.S.C. 165, apply
        "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=RTC&sectionNum=17201",
        # Cal. Rev. & Tax. Code § 17204(b): 26 U.S.C. 165(h)(5) shall not apply
        "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=RTC&sectionNum=17204",
        # 2024 Schedule CA (540) instructions, line 15
        "https://www.ftb.ca.gov/forms/2024/2024-540-booklet.pdf#page=66",
        # 2025 Schedule CA (540) instructions, line 15
        "https://www.ftb.ca.gov/forms/2025/2025-540-ca-instructions.html",
        # FTB Publication 1034, How to Calculate a Disaster Loss - Individuals
        # (2025 edition; the 2024 edition has the same text on the same page)
        "https://www.ftb.ca.gov/forms/misc/1034.pdf#page=4",
        "https://web.archive.org/web/20250529011540/https://www.ftb.ca.gov/forms/misc/1034.pdf#page=4",
        # 2024 Form 4684, lines 10-18
        "https://www.irs.gov/pub/irs-prior/f4684--2024.pdf#page=1",
    )
    defined_for = StateCode.CA
    documentation = """
    California adopts 26 U.S.C. 165 (R&TC 17201) but not the federal limit of
    personal casualty losses to declared disasters (R&TC 17204(b)). Schedule CA
    (540) line 15 has filers complete a second federal Form 4684 with California
    amounts, so a non-disaster personal casualty or theft loss stays
    deductible: each casualty is reduced by $100, and the rest is deductible
    above 10% of federal adjusted gross income.
    """

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.irs.deductions.itemized.casualty
        # California never applies the federal suspension: its IRC conformity
        # date was January 1, 2015 through 2024, before 26 U.S.C. 165(h)(5)
        # was enacted, and R&TC 17204(b) turns (h)(5) off from 2025.
        # Only the owner of the property claims the loss. A dependent's loss
        # belongs on the dependent's own return, as the dependent's income
        # does: adjusted gross income leaves it out.
        loss = tax_unit_non_dep_add(tax_unit, period, ["casualty_loss"])
        # Form 4684 line 11 reduces each casualty by $100. California states no
        # amount of its own; it takes 165(h)(1) through R&TC 17201. A joint
        # return is one individual for the $100 rule. The model records one
        # loss amount per person, not separate casualty events, so the
        # return's losses are treated as one casualty and the reduction
        # applies once.
        reduced_loss = max_(loss - p.per_casualty_reduction, 0)
        # Form 4684 line 17 and FTB Publication 1034: 10% of federal adjusted
        # gross income (Form 540 line 13), not California AGI.
        positive_agi = tax_unit("positive_agi", period)
        return max_(reduced_loss - positive_agi * p.floor, 0)
