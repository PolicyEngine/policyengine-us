from policyengine_us.model_api import *


class ny_itemized_deductions_phase_out(Variable):
    value_type = float
    entity = TaxUnit
    label = "New York itemized deductions pre-TCJA overall limitation"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/68",  # pre-TCJA IRC 68
        "https://www.nysenate.gov/legislation/laws/TAX/615",  # NY conformity
        "https://www.tax.ny.gov/pdf/current_forms/it/it196i.pdf#page=19",  # Line 40 worksheet
    )
    defined_for = "ny_itemized_deductions_phase_out_applies"
    documentation = """
    IT-196 Line 40, Total itemized deductions worksheet. This is the pre-TCJA
    federal "Pease" overall limitation on itemized deductions (26 U.S.C. 68 as
    it existed before Public Law 115-97), to which NY Tax Law 615 conforms.
    The limitation reduces itemized deductions by the LESSER OF:
      (a) 3% of federal AGI over the applicable amount (worksheet lines 5-8), or
      (b) 80% of the deductions that are subject to the limitation (lines 1-4).

    Mapping of the worksheet's line-total inputs to PolicyEngine variables
    (federal Form IT-196 line numbers in brackets):

    Worksheet line 1 (L1) = form lines 4, 9, 15, 19, 20, 28, 39, i.e. the total
    itemized deductions before the limitation. In PolicyEngine this is
    ny_itemized_deductions_max minus the NY-only college tuition addition
    (form line 48/43, which is added after line 40 and is not on this
    worksheet). Form line 39 ("other itemized deductions": gambling losses,
    estate tax on income in respect of a decedent, amortizable bond premium,
    federal disaster loss, etc.) is not modeled in PolicyEngine and is therefore
    treated as zero.

    Worksheet line 2 (L2) = form lines 4, 14, 16a, 20, 29, 30, 37, i.e. the
    deductions NOT subject to the limitation (26 U.S.C. 68(c)):
      - line 4  medical/dental        -> medical_expense_deduction
      - line 14 investment interest   -> investment_interest_expense
      - line 20 casualty/theft loss   -> ny_casualty_loss_deduction
      - lines 16a/29/30/37 (qualified contributions, gambling losses,
        income-producing-property casualty, federal disaster loss) are not
        separately modeled in PolicyEngine and are treated as zero.

    L3 = L1 - L2 (worksheet line 3) is therefore the mortgage interest, real
    estate taxes, charitable gifts, and 2%-floor miscellaneous deductions -
    exactly the 68(c) base subject to the limitation. Because investment
    interest appears in both L1 (inside interest_deduction) and L2, it cancels
    out of L3, as intended.
    """

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ny.tax.income.deductions.itemized.phase_out

        # Worksheet line 1 (L1): total itemized deductions before the limitation.
        # ny_itemized_deductions_max includes the NY-only college tuition
        # deduction (form line 48/43), which is added after line 40 and is not
        # part of this worksheet, so it is removed here.
        itemized_max = tax_unit("ny_itemized_deductions_max", period)
        college_tuition = tax_unit("ny_college_tuition_deduction", period)
        l1 = itemized_max - college_tuition

        # Worksheet line 2 (L2): deductions not subject to the limitation
        # (26 U.S.C. 68(c)) - medical, investment interest, casualty/theft.
        medical = tax_unit("medical_expense_deduction", period)
        investment_interest = add(tax_unit, period, ["investment_interest_expense"])
        casualty = tax_unit("ny_casualty_loss_deduction", period)
        l2 = medical + investment_interest + casualty

        # Worksheet line 3 (L3): deductions subject to the limitation. Floored at
        # zero to implement the worksheet's line-3 stop ("If line 2 is not less
        # than line 1, your deduction is not limited").
        l3 = max_(l1 - l2, 0)

        # Worksheet line 4 (L4): 80% of the limited deductions.
        l4 = l3 * p.deduction_limited_rate

        # Worksheet lines 5-8: 3% of federal AGI over the applicable amount.
        # The defined_for guard already restricts this to filers whose federal
        # AGI exceeds the applicable amount (worksheet line 7), so the excess is
        # positive; max_ guards the vectorized boundary.
        agi = tax_unit("adjusted_gross_income", period)
        filing_status = tax_unit("filing_status", period)
        applicable_amount = p.start[filing_status]
        agi_excess = max_(agi - applicable_amount, 0)
        l8 = agi_excess * p.agi_excess_rate

        # Worksheet lines 9-10: reduce by the smaller of the two limbs.
        return min_(l4, l8)
