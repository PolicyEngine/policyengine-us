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
        # MCA 15-30-2120(1), (2)(i)-(j): federal taxable income base and addbacks.
        "https://mca.legmt.gov/bills/mca/title_0150/chapter_0300/part_0210/section_0200/0150-0300-0210-0200.html",
        "https://mca.legmt.gov/bills/mca/title_0150/chapter_0300/part_0210/section_0010/0150-0300-0210-0010.html",
        "https://revenue.mt.gov/files/forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2024_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=15",
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
        # Tax units can claim the larger of the itemized or standard deductions
        deductions = max_(itemized_deductions, standard_deduction)
        exemptions = add(
            person.tax_unit,
            period,
            ["mt_personal_exemptions_joint", "mt_dependent_exemptions_person"],
        )

        return is_head * max_(0, total_agi - deductions - exemptions)

    def formula_2024(person, period, parameters):
        # MCA 15-30-2101(7) incorporates the subtraction-based IRC 63 base.
        # Worksheet A adjusts the deduction before Form 2 line 3's zero floor,
        # so deductions exceeding AGI can absorb the state-income-tax addback.
        tax_unit = person.tax_unit
        federal_base = (
            tax_unit("adjusted_gross_income", period)
            - tax_unit("exemptions", period)
            - tax_unit("taxable_income_deductions", period)
        )
        qbi_add_back = tax_unit("qualified_business_income_deduction", period)
        state_tax_add_back = tax_unit("mt_state_income_tax_itemized_add_back", period)
        federal_base = max_(0, federal_base + qbi_add_back + state_tax_add_back)
        # Form 2 applies Montana additions and subtractions after line 3.
        on_return = person("is_tax_unit_head_or_spouse", period)
        additions = tax_unit.sum(person("mt_additions", period) * on_return)
        subtractions = tax_unit.sum(person("mt_subtractions", period) * on_return)
        p = parameters(period).gov.states.mt.tax.income.subtractions
        if "mt_federal_obbba_subtraction" in p.subtractions:
            # Schedule 1-A deductions are already in federal taxable income.
            # The legacy AGI-based subtraction must not deduct them again.
            subtractions = subtractions - tax_unit.sum(
                person("mt_federal_obbba_subtraction", period) * on_return
            )
        is_head = person("is_tax_unit_head", period)
        return is_head * max_(
            0,
            federal_base + additions - subtractions,
        )
