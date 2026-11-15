from policyengine_us.model_api import *
from policyengine_us.tools.mt_separate_return import (
    mt_separate_tax_before_refundable_credits,
)

# Elections whose taxes differ by no more than this are treated as equal, so
# float32 noise does not decide between them.
TAX_TOLERANCE = 0.01


class mt_tax_unit_itemizes(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Whether the tax unit in Montana itemizes the deductions when married filing separately"
    documentation = (
        "The deduction election on the separate (status 2a) path. Spouses "
        "filing separately on the same form must both claim the standard "
        "deduction or both itemize, and the standard deduction is allowed if "
        "the taxpayer elects it, so the couple takes whichever election gives "
        "the lower combined tax before refundable credits (Form 2 line 20 in "
        "both columns), evaluated in closed form with the column variables' "
        "formulas. Itemizing uses the tax-minimizing split of the dependents' "
        "medical expenses (mt_dependent_medical_expense_head_share). When the "
        "two taxes are equal, the larger combined deduction decides, as it "
        "did before. The joint path does not read this variable: a single "
        "return takes the larger deduction, which cannot raise its tax. In "
        "years without separate filing on the same form, the larger combined "
        "deduction decides."
    )
    reference = (
        # 2022 Form 2 instructions, PDF page 11: spouses "must either both
        # claim the standard deduction, or both itemize their deductions".
        "https://revenuefiles.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2022_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=11",
        # MCA 2021 15-30-2132(1): the standard deduction "is allowed if
        # elected by the taxpayer".
        "https://mca.legmt.gov/bills/2022/mca/title_0150/chapter_0300/part_0210/section_0320/0150-0300-0210-0320.html",
    )
    definition_period = YEAR
    defined_for = StateCode.MT

    def formula(tax_unit, period, parameters):
        itemized = tax_unit.members("mt_itemized_deductions_indiv", period)
        standard = tax_unit.members("mt_standard_deduction_indiv", period)
        larger_itemized = tax_unit.sum(itemized) > tax_unit.sum(standard)
        p = parameters(period).gov.states.mt.tax.income
        if not p.married_filing_separately_on_same_return_allowed:
            return larger_itemized
        tax_itemizing = mt_separate_tax_before_refundable_credits(
            tax_unit, period, parameters, itemized
        )
        tax_standard = mt_separate_tax_before_refundable_credits(
            tax_unit, period, parameters, standard
        )
        tied = np.abs(tax_itemizing - tax_standard) <= TAX_TOLERANCE
        return where(tied, larger_itemized, tax_itemizing < tax_standard)
