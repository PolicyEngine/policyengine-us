from policyengine_us.model_api import *


class mt_salt_deduction(Variable):
    value_type = float
    entity = Person
    label = "Montana state and local tax deduction"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Itemized Deductions Schedule, line 5, for a return with one column: "
        "a single, head of household or joint return, or a married person "
        "filing on a separate form. Through 2023 the return's total is "
        "assigned to the tax unit head."
    )
    reference = (
        "https://revenuefiles.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2/2021_Montana_Individual_Income_Tax_Return_Form_2.pdf#page=7",
        "https://revenuefiles.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2/2022_Montana_Individual_Income_Tax_Return_Form_2.pdf#page=7",
        "https://revenuefiles.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2/2023_Montana_Individual_Income_Tax_Return_Form_2.pdf#page=7",
        "https://revenuefiles.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2021_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=32",
        "https://revenuefiles.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2022_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=34",
        "https://revenuefiles.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2023_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=37",
        "https://mca.legmt.gov/bills/2022/mca/title_0150/chapter_0300/part_0210/section_0310/0150-0300-0210-0310.html",
        # Former MCA 15-30-2131(1)(a)(ii) (2021): items under IRC 161, except
        # state income tax paid. The cap is 26 USC 164(b)(6).
    )
    defined_for = StateCode.MT

    def formula(person, period, parameters):
        p = parameters(period).gov.irs.deductions.itemized.salt_and_real_estate
        p_mt = parameters(period).gov.states.mt.tax.income.deductions.itemized
        filing_status = person.tax_unit("filing_status", period)
        cap = p.cap[filing_status]
        if p_mt.state_specific_deduction_applies:
            # Line 5 adds lines 5a through 5d for the whole return and caps
            # the total once: "not more than $10,000 if your status is
            # single, head of household or married filing jointly; or $5,000
            # if you are married filing separately".
            # 5a: general state and local sales taxes.
            # 5b: local income taxes. No Montana locality levies one, but
            #     a resident can owe another city's earnings or wage tax.
            # 5c: real estate taxes.
            # 5d: value-based personal property taxes, not modeled.
            taxes = add(
                person.tax_unit,
                period,
                [
                    "real_estate_taxes",
                    "state_sales_tax",
                    "local_sales_tax",
                    "local_income_tax",
                ],
            )
            is_head = person("is_tax_unit_head", period)
            return is_head * min_(taxes, cap)
        # From 2024 the schedule is discontinued. This keeps the earlier
        # per-person amounts until the 2024 Form 2 line 2 is modeled.
        real_estate_tax = person("real_estate_taxes", period)
        return min_(real_estate_tax, cap)
