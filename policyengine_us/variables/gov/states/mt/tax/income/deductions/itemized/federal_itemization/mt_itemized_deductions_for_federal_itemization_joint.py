from policyengine_us.model_api import *


class mt_itemized_deductions_for_federal_itemization_joint(Variable):
    value_type = float
    entity = Person
    label = "Montana itemized deductions when married couples are filing jointly"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://revenuefiles.mt.gov/files/forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2021_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=33",
        # 2021 Form 2 line 9 includes qualified mortgage insurance premiums
        # allowed on the federal return, after the federal AGI phase-out.
        "https://revenuefiles.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2/2022_Montana_Individual_Income_Tax_Return_Form_2.pdf#page=7",
        "https://law.justia.com/codes/montana/2022/title-15/chapter-30/part-21/section-15-30-2131/",
        # MT Code § 15-30-2131 (2022) (1)
        "https://mca.legmt.gov/bills/2019/mca/title_0150/chapter_0300/part_0210/section_0010/0150-0300-0210-0010.html",
        # MCA 15-30-2101: "Internal Revenue Code" means the IRC as amended
        "https://revenuefiles.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2023_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=38",
        # 2023 Form 2 instructions, itemized deductions line 9: home mortgage
        # interest "allowed by federal law", limited to the first $750,000 of
        # acquisition debt incurred after Dec. 15, 2017
        "https://revenuefiles.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2024_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=15",
        # 2024 Form 2 instructions, line 2 and Worksheet A: adjusted federal
        # itemized deductions
    )
    defined_for = StateCode.MT

    def formula(person, period, parameters):
        is_head = person("is_tax_unit_head", period)
        p = parameters(period).gov.states.mt.tax.income.deductions.itemized
        if not p.state_specific_deduction_applies:
            # From 2024 there is no federal income tax deduction, so this
            # equals mt_itemized_deductions_joint.
            adjusted_federal_itemized_deductions = person.tax_unit(
                "mt_adjusted_federal_itemized_deductions", period
            )
            return is_head * adjusted_federal_itemized_deductions
        charitable_deduction = person.tax_unit("charitable_deduction", period)
        investment_interest = person("investment_interest_expense", period)
        # A joint return deducts the interest either spouse paid, excluding
        # dependents. Montana allows only mortgage interest federal law
        # allows (MCA 15-30-2131(1)(a); Form 2 itemized deductions line 9).
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        mortgage_interest = person.tax_unit.sum(
            head_or_spouse * person("deductible_mortgage_interest", period)
        )
        # The joint return includes the federal premium deduction for both
        # spouses, once, in the head's itemized deduction total.
        mortgage_insurance = person.tax_unit(
            "deductible_mortgage_insurance_premiums", period
        )
        interest_ded = (
            person.tax_unit.sum(head_or_spouse * investment_interest)
            + mortgage_interest
            + mortgage_insurance
        )
        other_deductions = add(
            person.tax_unit,
            period,
            [
                "mt_misc_deductions",
                "mt_child_dependent_care_expense_deduction_joint",
                "mt_medical_expense_deduction_joint",
                "mt_salt_deduction",
                "mt_federal_income_tax_deduction_for_federal_itemization",
            ],
        )
        return is_head * (interest_ded + other_deductions + charitable_deduction)
