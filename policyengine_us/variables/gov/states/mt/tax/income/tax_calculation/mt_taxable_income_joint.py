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
        "https://revenuefiles.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2/2024_Montana_Individual_Income_Tax_Return_Form_2.pdf#page=1",
        "https://revenuefiles.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2/2025_Montana_Individual_Income_Tax_Return_Form_2.pdf#page=1",
    )

    def formula(person, period, parameters):
        is_head = person("is_tax_unit_head", period)

        if parameters(period).gov.states.mt.tax.income.federal_taxable_income_base:
            federal_taxable_income = person.tax_unit(
                "mt_federal_taxable_income", period
            )
            additions = add(person.tax_unit, period, ["mt_additions"])
            subtractions = add(person.tax_unit, period, ["mt_subtractions"])
            return is_head * max_(0, federal_taxable_income + additions - subtractions)

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
