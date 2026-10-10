from policyengine_us.model_api import *


class mt_itemized_deductions_joint(Variable):
    value_type = float
    entity = Person
    label = "Montana itemized deductions when married couples are filing jointly"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://revenuefiles.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2/2022_Montana_Individual_Income_Tax_Return_Form_2.pdf#page=7",
        "https://law.justia.com/codes/montana/2022/title-15/chapter-30/part-21/section-15-30-2131/",
        # MT Code § 15-30-2131 (2022) (1)
        "https://mca.legmt.gov/bills/2019/mca/title_0150/chapter_0300/part_0210/section_0010/0150-0300-0210-0010.html",
        # MCA 15-30-2101: "Internal Revenue Code" means the IRC as amended
        "https://revenuefiles.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2023_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=38",
        # 2023 Form 2 instructions, itemized deductions line 9: home mortgage
        # interest "allowed by federal law", limited to the first $750,000 of
        # acquisition debt incurred after Dec. 15, 2017
    )
    defined_for = StateCode.MT

    def formula(person, period, parameters):
        charitable_deduction = person.tax_unit("charitable_deduction", period)
        investment_interest = person("investment_interest_expense", period)
        # Montana allows the mortgage interest federal law allows, so interest
        # on acquisition debt above the IRC 163(h)(3) caps is not deductible
        # (MCA 15-30-2131(1)(a); Form 2 instructions, itemized line 9).
        mortgage_interest = person("deductible_mortgage_interest", period)
        interest_ded = investment_interest + mortgage_interest
        other_deductions = add(
            person.tax_unit,
            period,
            [
                "mt_misc_deductions",
                "mt_medical_expense_deduction_joint",
                "mt_salt_deduction",
                "mt_federal_income_tax_deduction_unit",
            ],
        )
        is_head = person("is_tax_unit_head", period)
        return is_head * (interest_ded + other_deductions + charitable_deduction)
