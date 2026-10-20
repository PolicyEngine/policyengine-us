from policyengine_us.model_api import *


def get_ny_recomputed_branch(tax_unit, period):
    """
    The branch whose federal adjusted gross income is New York's recomputed
    federal AGI (Form IT-201 line 19a), or None when the two are equal for
    every tax unit.

    New York matches federal credits computed with line 19a (the IT-213 and
    IT-215 recomputations). The only Form IT-558 adjustment modeled is A-003,
    the 2020 federal charitable deduction for non-itemizers, so the branch
    sets that deduction to zero and keeps each unit's federal itemization
    choice.
    """
    deduction = tax_unit("charitable_contributions_ald", period)
    if not deduction.any():
        return None
    return get_override_branch(
        tax_unit.simulation,
        "ny_recomputed_federal_agi",
        period,
        {
            "charitable_contributions_ald": np.zeros(tax_unit.count),
            "tax_unit_itemizes": tax_unit("tax_unit_itemizes", period),
        },
    )


class ny_recomputed_federal_agi(Variable):
    value_type = float
    entity = TaxUnit
    label = "New York recomputed federal adjusted gross income"
    unit = USD
    documentation = (
        "Federal adjusted gross income as reported, plus the Form IT-558 "
        "addition adjustments and less its subtraction adjustments (Form "
        "IT-201 line 19a). New York AGI, the credits and the itemized "
        "deduction floors and limitation start from it. The adjustment "
        "modeled is A-003: the 2020 federal charitable deduction for "
        "non-itemizers (IRC 62(a)(22)), which New York did not adopt."
    )
    definition_period = YEAR
    reference = (
        # 2020 IT-201 instructions, line 19a worksheet.
        "https://www.tax.ny.gov/pdf/2020/inc/it201i_2020.pdf#page=16",
        # 2020 IT-558 instructions, addition A-003.
        "https://www.tax.ny.gov/pdf/2020/inc/it558i_2020.pdf#page=2",
    )
    # Not limited to New York: its readers are, and New York City residents
    # are New York residents.

    adds = ["adjusted_gross_income", "charitable_contributions_ald"]
