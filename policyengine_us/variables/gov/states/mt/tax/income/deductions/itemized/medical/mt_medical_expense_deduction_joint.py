from policyengine_us.model_api import *


class mt_medical_expense_deduction_joint(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "Montana medical expense deduction when married couples are filing jointly"
    reference = (
        "https://revenuefiles.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2/2022_Montana_Individual_Income_Tax_Return_Form_2.pdf#page=7",
        "https://revenuefiles.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2022_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=32",
        "https://revenuefiles.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2024_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=15",
        "https://law.justia.com/codes/montana/2022/title-15/chapter-30/part-21/section-15-30-2131/",
        # MT Code § 15-30-2131 (2022) (1)(a)
    )
    unit = USD
    defined_for = StateCode.MT

    def formula(person, period, parameters):
        p = parameters(period).gov.states.mt.tax.income.deductions.itemized
        if p.state_specific_deduction_applies:
            expense = person.tax_unit("itemized_medical_expenses", period)
            floor = parameters(period).gov.irs.deductions.itemized.medical.floor
            # Itemized Deductions Schedule line 1b takes Montana AGI from
            # page 1, line 14. A joint return reports that line in a single
            # column, so the floor applies to the return's pooled Montana AGI.
            montana_agi = person.tax_unit("mt_agi_joint", period)
            deduction = max_(0, expense - floor * montana_agi)
        else:
            # From 2024, Form 2 line 2 takes federal itemized deductions
            # (Worksheet A), so the federal floor on federal AGI applies.
            deduction = person.tax_unit("medical_expense_deduction", period)
        is_head = person("is_tax_unit_head", period)
        return is_head * deduction
