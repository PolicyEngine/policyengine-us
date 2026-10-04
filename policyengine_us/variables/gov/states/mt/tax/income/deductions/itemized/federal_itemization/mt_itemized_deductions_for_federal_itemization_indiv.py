from policyengine_us.model_api import *


class mt_itemized_deductions_for_federal_itemization_indiv(Variable):
    value_type = float
    entity = Person
    label = "Montana itemized deductions when married couples are filing separately"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://revenuefiles.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2/2022_Montana_Individual_Income_Tax_Return_Form_2.pdf#page=7",
        "https://law.justia.com/codes/montana/2022/title-15/chapter-30/part-21/section-15-30-2131/",
        # MT Code § 15-30-2131 (2022) (1)
        "https://revenue.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2023_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=31",
        "https://revenue.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2/2024_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=7",
    )
    defined_for = "mt_married_filing_separately_on_same_return_eligible"
    documentation = """
    The 2023 Form 2 instructions, line 10, say to determine investment
    interest by "following the computation on federal Form 4952 but include
    any Montana adjustments to income." Worksheet A line 1 of the 2024
    instructions says, "Enter your total federal itemized deductions from
    Form 1040, line 12."

    Investment interest uses federal Form 4952 line 8. Before 2024 this is an
    approximation: the 2023 instructions call for federal Form 4952
    "separately", and Montana investment-income adjustments are not modeled.
    The model allocates the tax-unit deduction by each person's share of
    investment interest paid for separate filing on the same return.
    """

    def formula(person, period, parameters):
        p = parameters(period).gov.irs.deductions
        # Since we only compute the federal charitable deduction at the tax unit level,
        # we will split the value between each spouse
        charitable_deduction = person.tax_unit("charitable_deduction", period) * 0.5
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        # Allocate federal Form 4952 line 8 by each person's share of interest paid.
        interest_paid = person("investment_interest_expense", period)
        total_interest_paid = person.tax_unit.sum(interest_paid)
        interest_share = np.divide(
            interest_paid,
            total_interest_paid,
            out=np.zeros_like(interest_paid),
            where=total_interest_paid > 0,
        )
        investment_interest = (
            person.tax_unit("investment_interest_expense_deduction", period)
            * interest_share
        )
        mortgage_interest = person("mortgage_interest", period)
        interest_ded = investment_interest + mortgage_interest
        other_deductions = add(
            person,
            period,
            [
                "mt_misc_deductions",
                "mt_medical_expense_deduction_indiv",
                "mt_salt_deduction",
                "mt_federal_income_tax_deduction_for_federal_itemization_indiv",
            ],
        )
        return head_or_spouse * (interest_ded + charitable_deduction + other_deductions)
