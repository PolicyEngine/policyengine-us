from policyengine_us.model_api import *


def get_ny_recomputed_branch(tax_unit, period, keep_federal_tax=False):
    """
    The branch whose federal adjusted gross income is New York's recomputed
    federal AGI (Form IT-201 line 19a), or None when the two are equal for
    every tax unit.

    New York matches federal credits computed with line 19a (the IT-213 and
    IT-215 recomputations). Line 19a is federal AGI as reported plus the Form
    IT-558 additions, of which the model has one, A-003, the 2020 federal
    charitable deduction for non-itemizers. Nothing else on the federal
    return is recomputed, so the branch sets adjusted gross income to line
    19a and keeps each unit's federal itemization choice. The deduction is
    zero in the branch, which already counts it in adjusted gross income.

    With ``keep_federal_tax``, the branch also keeps income tax before
    credits (Form 1040 line 18), which IT-213 Worksheet A takes as reported.
    The EITC does not need it, and New York City's EITC must not read it:
    New York City income tax enters the federal deduction for state and
    local taxes.
    """
    deduction = tax_unit("charitable_contributions_ald", period)
    if not deduction.any():
        return None
    overrides = {
        "adjusted_gross_income": tax_unit("ny_recomputed_federal_agi", period),
        "charitable_contributions_ald": np.zeros(tax_unit.count),
        "tax_unit_itemizes": tax_unit("tax_unit_itemizes", period),
    }
    name = "ny_recomputed_federal_agi"
    if keep_federal_tax:
        overrides["income_tax_before_credits"] = tax_unit(
            "income_tax_before_credits", period
        )
        name = "ny_recomputed_federal_agi_with_federal_tax"
    return get_override_branch(tax_unit.simulation, name, period, overrides)


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
