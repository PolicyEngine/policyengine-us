from policyengine_us.model_api import *


class mt_taxable_income_joint(Variable):
    value_type = float
    entity = Person
    label = "Montana taxable income when married couples file jointly"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MT
    reference = (
        "https://revenuefiles.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2/2022_Montana_Individual_Income_Tax_Return_Form_2.pdf#page=1",
        "https://revenuefiles.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2022_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=16",
        # MCA 15-30-2120(1): from 2024 Montana starts from federal taxable income
        "https://mca.legmt.gov/bills/mca/title_0150/chapter_0300/part_0210/section_0200/0150-0300-0210-0200.html",
        # 2024 Form 2 instructions, line 2: "You must use the same type of
        # deduction taken on your federal return"
        "https://revenuefiles.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2024_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=15",
        # 26 U.S.C. 63(b)(4): a non-itemizer also deducts the section 170(p)
        # charitable contributions
        "https://www.law.cornell.edu/uscode/text/26/63#b_4",
    )

    def formula(person, period, parameters):
        is_head = person("is_tax_unit_head", period)

        # For joint filers, use mt_agi_joint which pools income and subtractions
        # at tax unit level before applying them. This ensures subtractions from
        # one spouse can offset income from the other spouse.
        total_agi = person.tax_unit("mt_agi_joint", period)

        standard_deduction = add(
            person.tax_unit, period, ["mt_standard_deduction_joint"]
        )
        itemized_deductions = add(
            person.tax_unit, period, ["mt_itemized_deductions_joint"]
        )
        p = parameters(period).gov.states.mt.tax.income.deductions.itemized
        if p.state_specific_deduction_applies:
            # Tax units can claim the larger of the itemized or standard deductions
            deductions = max_(itemized_deductions, standard_deduction)
        else:
            # Federal taxable income carries the deduction type of the federal
            # return, and a federal non-itemizer's section 170(p) deduction.
            itemizes = person.tax_unit("tax_unit_itemizes", period)
            non_itemizer_charitable_deduction = person.tax_unit(
                "charitable_deduction_for_non_itemizers", period
            )
            deductions = where(
                itemizes,
                itemized_deductions,
                standard_deduction + non_itemizer_charitable_deduction,
            )
        exemptions = add(
            person.tax_unit,
            period,
            ["mt_personal_exemptions_joint", "mt_dependent_exemptions_person"],
        )

        return is_head * max_(0, total_agi - deductions - exemptions)
