from policyengine_us.model_api import *


class mt_elderly_homeowner_or_renter_credit_federal_refundable_credits(Variable):
    value_type = float
    entity = Person
    label = "Federal refundable credits in Montana elderly homeowner/renter credit gross household income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MT
    reference = (
        # ARM 42.4.301(2)(b): "federal refundable tax credits received"
        "https://rules.mt.gov/api/policy-library-public/collections/aec52c46-128e-4279-9068-8af5d5432d74/policies/c90ea93a-03a2-4605-a0f8-f2f3760198bf/document/768c8344-24ee-4950-9d5e-9d8fc97ec0f7",
        # 2023 instructions, line 7: "the federal and Montana Earned Income Tax
        # Credit, the federal Child Tax Credits"
        "https://revenue.mt.gov/files/forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2023_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=51",
        # 2024 Schedule 2EC, line 8: "the federal and Montana earned income tax
        # credits, the refundable portion of the federal child tax credit"
        "https://revenue.mt.gov/files/forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2024_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=47",
    )

    def formula(person, period, parameters):
        # Federal refundable credits are claimed on the tax unit's return.
        # Gross household income sums this person-level amount over the
        # household, so count each return's credits once, on its head.
        head = person("is_tax_unit_head", period)
        return head * person.tax_unit("income_tax_refundable_credits", period)
