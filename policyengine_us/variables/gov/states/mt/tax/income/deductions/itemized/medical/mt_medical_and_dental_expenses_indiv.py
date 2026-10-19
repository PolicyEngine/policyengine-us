from policyengine_us.model_api import *


class mt_medical_and_dental_expenses_indiv(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "Montana medical and dental expenses in each column when married couples are filing separately"
    documentation = (
        "Itemized Deductions Schedule line 1a in a filer's column: medical "
        "and dental expenses other than insurance premiums. Other medical "
        "expenses are recorded on the person cared for, including amounts "
        "other household members paid on that person's behalf, so the "
        "inputs do not say which spouse paid a dependent's bills. Each "
        "spouse's own expenses stay in that spouse's column. A dependent's "
        "expenses are divided equally between spouses filing separately on "
        "the same form, the model's convention for itemized deductions not "
        "clearly attributable to one spouse; the form lets the couple divide "
        "them in any proportion. An unmarried filer's column holds every "
        "dependent's expenses. The head's and spouse's columns together hold "
        "every member's other medical expenses, as the joint return's line 1 "
        "does."
    )
    reference = (
        "https://revenuefiles.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2/2022_Montana_Individual_Income_Tax_Return_Form_2.pdf#page=7",
        # PDF pages 11, 32. Page 11, "Allocation of deductions": payments
        # from accounts owned by both spouses for expenses not attributable
        # specifically to one spouse "can be allocated to either spouse in
        # any proportional amount". Page 32: line 1 instructions.
        "https://revenuefiles.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2022_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=11",
        # ARM 42.15.524(3)(a)-(b), in effect 2010-2024 (repealed effective
        # Jan. 25, 2025): a deduction clearly attributable to one spouse is
        # claimed only by that spouse; on the same form, one not clearly
        # attributable to one spouse "may be divided as provided on the form".
        "https://web.archive.org/web/20201030190413/http://www.mtrules.org/gateway/ruleno.asp?RN=42.15.524",
        # MCA 2021 § 15-30-2131(1)(a)
        "https://mca.legmt.gov/bills/2022/mca/title_0150/chapter_0300/part_0210/section_0310/0150-0300-0210-0310.html",
    )
    unit = USD
    defined_for = "mt_married_filing_separately_on_same_return_eligible"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.mt.tax.income.deductions.itemized
        expense = person("other_medical_expenses", period)
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        dependent_expense = person.tax_unit.sum(expense * ~head_or_spouse)
        married = person.tax_unit("tax_unit_married", period)
        head = person("is_tax_unit_head", period)
        share = where(married, head_or_spouse * p.spouse_allocation_rate, head)
        return head_or_spouse * expense + share * dependent_expense
