from policyengine_us.model_api import *


class mt_elderly_homeowner_or_renter_credit_federal_refundable_credits(Variable):
    value_type = float
    entity = Person
    label = "Federal refundable credits received, in Montana elderly homeowner/renter credit gross household income"
    documentation = (
        "Federal refundable tax credit cash this person received during the "
        "year: the return's recovery rebate credits (the 2020 and 2021 "
        "Economic Impact Payments, advanced during the same year) on the tax "
        "unit head, plus "
        "mt_elderly_homeowner_or_renter_credit_other_federal_refundable_credits, "
        "the other federal refundable credits received, such as an earned "
        "income or child tax credit refund from the prior year's return. The "
        "other credits claimed on this year's return are paid after the year "
        "ends, so they do not establish a receipt. Record other receipts in "
        "that input. An input to this variable replaces the computed amount "
        "for everyone and sets anyone not given a value to 0, so supply it "
        "for every household member, for example to record that a return "
        "received no payment."
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
        # 2021 instructions, line 7: "Combine all the refundable credits
        # received by the members of the household in 2021", including "the
        # federal Child Tax Credits, Economic Impact Payments"
        "https://revenue.mt.gov/files/forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2021_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=49",
        # 2023 instructions, line 7: "Combine all the refundable credits
        # received by the members of the household in 2023", including "the
        # federal and Montana Earned Income Tax Credit, the federal Child Tax
        # Credits"
        "https://revenue.mt.gov/files/forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2023_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=51",
        # 2024 Schedule 2EC, line 8: "the federal and Montana earned income tax
        # credits, the refundable portion of the federal child tax credit"
        "https://revenue.mt.gov/files/forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2024_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=47",
    )

    # An actual-receipt amount, like mt_elderly_homeowner_or_renter_credit_received.
    # The refundable credits on this year's return, income_tax_refundable_credits,
    # are an entitlement paid in a later year, not a receipt during this one.
    # Reading last year's return instead would rerun the whole prior-year
    # federal tax computation for each record, and it reads 0 whenever the
    # inputs cover only one year.
    #
    # The recovery rebate credits are the exception. IRC 6428(f), 6428A(f)
    # and 6428B(g) paid them in advance as Economic Impact Payments, by
    # December 31, 2020 (CARES), January 15, 2021 (CAA) and December 31,
    # 2021 (ARPA), so each year's credit was received in that year. The
    # CAA credit is a 2020 credit whose advance could run to January 15,
    # 2021; it is counted in 2020 with the CARES payment. The return's
    # credit stands in for the advance payment; any amount reconciled on the
    # return is paid the next year and is not separated here. The credit
    # parameters are zero outside 2020 and 2021, so so is this default.
    #
    # Not counted by default: the 2021 advance child tax credit. IRC 7527A
    # advanced half of the estimated 2021 child tax credit in monthly
    # payments from July to December 2021, and the 2021 instructions list
    # "the federal Child Tax Credits" among the credits received. The model
    # does not compute the advance payments, so a household that received
    # them records them in
    # mt_elderly_homeowner_or_renter_credit_other_federal_refundable_credits.
    #
    # Other receipts come from that separate input, so supplying one
    # person's leaves every other return's default payments in place.
    def formula(person, period, parameters):
        # Gross household income sums this person-level amount over the
        # household, so count each return's payments once, on its head.
        head = person("is_tax_unit_head", period)
        payments = head * person.tax_unit("recovery_rebate_credit", period)
        other = person(
            "mt_elderly_homeowner_or_renter_credit_other_federal_refundable_credits",
            period,
        )
        return payments + other
