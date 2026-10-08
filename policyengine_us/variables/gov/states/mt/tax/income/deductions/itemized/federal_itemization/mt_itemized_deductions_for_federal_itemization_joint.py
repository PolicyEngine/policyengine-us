from policyengine_us.model_api import *


class mt_itemized_deductions_for_federal_itemization_joint(Variable):
    value_type = float
    entity = Person
    label = "Montana itemized deductions when married couples are filing jointly"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://revenuefiles.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2/2022_Montana_Individual_Income_Tax_Return_Form_2.pdf#page=7",
        "https://law.justia.com/codes/montana/2022/title-15/chapter-30/part-21/section-15-30-2131/",
        # MT Code § 15-30-2131 (2022) (1)
        "https://revenue.mt.gov/files/forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2023_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=38",
        "https://revenue.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2/2024_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=7",
    )
    defined_for = StateCode.MT
    documentation = """
    The 2023 Form 2 instructions, line 10, say to determine investment
    interest by "following the computation on federal Form 4952 but include
    any Montana adjustments to income." Worksheet A line 1 of the 2024
    instructions says, "Enter your total federal itemized deductions from
    Form 1040, line 12."

    Investment interest uses federal Form 4952 line 8. Before 2024 this is an
    approximation because Montana investment-income adjustments are not
    separately modeled. For joint filing the whole tax-unit investment
    interest deduction, including the spouse's amount, is assigned to the head.
    """

    def formula(person, period, parameters):
        charitable_deduction = person.tax_unit("charitable_deduction", period)
        investment_interest = person.tax_unit(
            "investment_interest_expense_deduction", period
        )
        mortgage_interest = person("mortgage_interest", period)
        interest_ded = investment_interest + mortgage_interest
        other_deductions = add(
            person.tax_unit,
            period,
            [
                "mt_misc_deductions",
                "mt_medical_expense_deduction_joint",
                "mt_salt_deduction",
                "mt_federal_income_tax_deduction_for_federal_itemization",
            ],
        )
        is_head = person("is_tax_unit_head", period)
        return is_head * (interest_ded + other_deductions + charitable_deduction)
