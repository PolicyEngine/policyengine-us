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
    )
    defined_for = StateCode.MT

    def formula(person, period, parameters):
        charitable_deduction = person.tax_unit("charitable_deduction", period)
        # A joint return deducts the interest either spouse paid, not a
        # dependent's own.
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        interest_ded = person.tax_unit.sum(
            head_or_spouse
            * add(person, period, ["investment_interest_expense", "mortgage_interest"])
        )
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
