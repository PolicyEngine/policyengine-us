from policyengine_us.model_api import *


class mt_itemized_deductions_indiv(Variable):
    value_type = float
    entity = Person
    label = "Montana itemized deductions when married couples are filing separately"
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
    )
    defined_for = "mt_married_filing_separately_on_same_return_eligible"

    def formula(person, period, parameters):
        # The medical deduction is kept apart because the split of a
        # dependent's medical bills is chosen by comparing the couple's tax
        # with every other itemized deduction held fixed
        # (mt_dependent_medical_expense_head_share).
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        medical = person("mt_medical_expense_deduction_indiv", period)
        return (
            person("mt_non_medical_itemized_deductions_indiv", period)
            + head_or_spouse * medical
        )
