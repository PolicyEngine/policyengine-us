from policyengine_us.model_api import *


class ny_casualty_loss_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "NY casualty loss deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.nysenate.gov/legislation/laws/TAX/615",
        # Filers use recomputed federal AGI on the 2020 IT-196 worksheet.
        "https://www.tax.ny.gov/pdf/2020/inc/it196i_2020.pdf#page=4",
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
    New York follows the 2017 federal rules for casualty and theft losses.
    Filers subtract $100 per casualty and deduct the remainder above 10%
    of New York's recomputed federal adjusted gross income.
    The formula reads current federal reduction and floor parameters, so
    federal parameter reforms also affect New York.
    """

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.irs.deductions.itemized.casualty
        # NY uses pre-TCJA rules: casualty losses are still deductible (not
        # limited to federally declared disasters like federal post-2017), so
        # the federal suspension flag does not apply.
        # A dependent's own loss belongs on the dependent's return.
        loss = tax_unit_non_dep_add(tax_unit, period, ["casualty_loss"])
        # Worksheet line 11 reduces each casualty by $100. A joint return is
        # one individual for the $100 rule. The model records one loss amount
        # per person, not separate casualty events, so the return's losses are
        # treated as one casualty and the reduction applies once.
        reduced_loss = max_(loss - p.per_casualty_reduction, 0)
        # IT-196 worksheet line 17 uses New York's recomputed federal AGI.
        positive_agi = max_(0, tax_unit("ny_recomputed_federal_agi", period))
        return max_(reduced_loss - positive_agi * p.floor, 0)
