from policyengine_us.model_api import *


class ny_casualty_loss_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "NY casualty loss deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.nysenate.gov/legislation/laws/TAX/615",
        # 2025 Form IT-196 instructions, line 20 and the Casualty and theft
        # worksheet, Section A
        "https://www.tax.ny.gov/pdf/2025/inc/it196i_2025.pdf#page=3",
        "https://www.tax.ny.gov/pdf/2025/inc/it196i_2025.pdf#page=4",
        "https://www.tax.ny.gov/pdf/2024/inc/it196i_2024.pdf#page=3",
        "https://www.tax.ny.gov/pdf/2024/inc/it196i_2024.pdf#page=4",
        # IRS Publication 547 (2017), $100 Rule
        "https://www.irs.gov/pub/irs-prior/p547--2017.pdf#page=10",
    )
    defined_for = StateCode.NY
    documentation = """
    NY Tax Law § 615 requires itemized deductions to be computed using
    pre-TCJA federal rules. Form IT-196 line 20 figures the casualty and theft
    loss "using the federal rules that applied to tax year 2017", so, unlike the
    federal deduction after 2017, it is not limited to federally declared
    disasters. Each casualty is reduced by $100, and the rest is deductible
    above 10% of federal adjusted gross income.
    """

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.irs.deductions.itemized.casualty
        # NY uses pre-TCJA rules: casualty losses are still deductible (not
        # limited to federally declared disasters like federal post-2017), so
        # the federal suspension flag does not apply.
        # Only the owner of the property claims the loss. A dependent's loss
        # belongs on the dependent's own return, as the dependent's income
        # does: federal adjusted gross income leaves it out.
        loss = tax_unit_non_dep_add(tax_unit, period, ["casualty_loss"])
        # Worksheet line 11 reduces each casualty by $100. A joint return is
        # one individual for the $100 rule. The model records one loss amount
        # per person, not separate casualty events, so the return's losses are
        # treated as one casualty and the reduction applies once.
        reduced_loss = max_(loss - p.per_casualty_reduction, 0)
        # Worksheet line 17: 10% of federal adjusted gross income (Form IT-201,
        # line 19).
        positive_agi = tax_unit("positive_agi", period)
        return max_(reduced_loss - positive_agi * p.floor, 0)
