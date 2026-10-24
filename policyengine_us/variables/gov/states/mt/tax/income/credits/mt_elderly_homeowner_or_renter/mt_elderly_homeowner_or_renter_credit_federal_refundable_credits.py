from policyengine_us.model_api import *


class mt_elderly_homeowner_or_renter_credit_federal_refundable_credits(Variable):
    value_type = float
    entity = Person
    label = "Federal refundable credits received, in Montana elderly homeowner/renter credit gross household income"
    documentation = (
        "Federal refundable tax credit cash this person received during the "
        "year, such as an earned income or child tax credit refund from the "
        "prior year's return or an Economic Impact Payment. Defaults to zero: "
        "the credits claimed on this year's return are paid after the year "
        "ends, so they do not establish a receipt."
    )
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MT
    reference = (
        # MCA 15-30-2337(4): gross household income is "all income received
        # by all individuals of a household"
        "https://mca.legmt.gov/bills/mca/title_0150/chapter_0300/part_0230/section_0370/0150-0300-0230-0370.html",
        # ARM 42.4.301(2)(b): "federal refundable tax credits received"
        "https://rules.mt.gov/api/policy-library-public/collections/aec52c46-128e-4279-9068-8af5d5432d74/policies/c90ea93a-03a2-4605-a0f8-f2f3760198bf/document/768c8344-24ee-4950-9d5e-9d8fc97ec0f7",
        # 2023 instructions, line 7: "Combine all the refundable credits
        # received by the members of the household in 2023", including "the
        # federal and Montana Earned Income Tax Credit, the federal Child Tax
        # Credits"
        "https://revenue.mt.gov/files/forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2023_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=51",
        # 2024 Schedule 2EC, line 8: "the federal and Montana earned income tax
        # credits, the refundable portion of the federal child tax credit"
        "https://revenue.mt.gov/files/forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2024_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=47",
    )

    # An actual-receipt input, like mt_elderly_homeowner_or_renter_credit_received.
    # The refundable credits on this year's return, income_tax_refundable_credits,
    # are an entitlement paid in a later year, not a receipt during this one.
    # Reading last year's return instead would rerun the whole prior-year
    # federal tax computation for each record, and it reads 0 whenever the
    # inputs cover only one year.
