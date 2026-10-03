from policyengine_us.model_api import *


class mt_refundable_credits(Variable):
    value_type = float
    entity = Person
    label = "Montana refundable credits"
    unit = USD
    reference = (
        # 2021 Montana Form 2 instructions, Other Payments and Refundable
        # Credits Schedule
        "https://revenuefiles.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2021_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=50",
        # Montana HB 192 (Ch. 44, L. 2023), enrolled bill, Sec. 2(1) and (3):
        # 2021 income tax rebate issued by December 31, 2023
        "https://web.archive.org/web/20230626082025/https://leg.mt.gov/bills/2023/billpdf/HB0192.pdf#page=1",
        # Montana Department of Revenue rebate report, May 2024, printed p. 8:
        # income tax rebates issued from July 3, 2023
        "https://archive.legmt.gov/content/Committees/Interim/2023-2024/Revenue/Meetings/May-2024/5.1-DOR-rebate-report.pdf#page=10",
    )
    definition_period = YEAR
    defined_for = StateCode.MT
    adds = [
        "mt_refundable_credits_before_renter_credit",
        "mt_elderly_homeowner_or_renter_credit",
        # HB 192 Sec. 2(1) has the 2021 income tax rebate issued by December
        # 31, 2023, and Sec. 2(3) pays it electronically or by check. By
        # PolicyEngine convention, as with Georgia's HB 162 surplus rebate, it
        # is booked to tax year 2021 as a refundable payment (zero in every
        # other year). It stays out of credits/refundable.yaml because that
        # list also feeds the elderly homeowner or renter credit's gross
        # household income (Form 2EC line 7).
        "mt_income_tax_rebate",
    ]
    # Under the gross income sources computation, the elderly homeowner or renter credit
    # is included in the list of refundable credits
    # This will create a potential circular reference (check reference Line7)
    # mt_refundable_credits_before_renter_credit was created to circumvent this
