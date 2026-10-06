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
        # MCA 2021 § 15-30-2131(1)(a) and (1)(g)
        "https://mca.legmt.gov/bills/2022/mca/title_0150/chapter_0300/part_0210/section_0310/0150-0300-0210-0310.html",
    )
    unit = USD
    defined_for = StateCode.MT

    def formula(person, period, parameters):
        p = parameters(period).gov.states.mt.tax.income.deductions.itemized
        if p.state_specific_deduction_applies:
            tax_unit = person.tax_unit
            floor = parameters(period).gov.irs.deductions.itemized.medical.floor
            # Itemized Deductions Schedule line 1 takes medical and dental
            # expenses other than the insurance premiums deducted in full on
            # lines 2 and 3.
            expense = add(tax_unit, period, ["other_medical_expenses"])
            # Line 1b takes Montana AGI from page 1, line 14. A joint return
            # reports that line in a single column, so the floor applies to
            # the return's pooled Montana AGI.
            montana_agi = tax_unit("mt_agi_joint", period)
            floored_expense = max_(0, expense - floor * montana_agi)
            # Line 2: medical insurance premiums not deducted elsewhere.
            # Line 3: long-term care insurance premiums, without the federal
            # age-based limit.
            premiums = add(
                tax_unit,
                period,
                [
                    "mt_eligible_medical_insurance_premiums",
                    "long_term_health_insurance_premiums",
                ],
            )
            deduction = floored_expense + premiums
        else:
            # From 2024, Form 2 line 2 takes federal itemized deductions
            # (Worksheet A), so the federal floor on federal AGI applies.
            deduction = person.tax_unit("medical_expense_deduction", period)
        is_head = person("is_tax_unit_head", period)
        return is_head * deduction
