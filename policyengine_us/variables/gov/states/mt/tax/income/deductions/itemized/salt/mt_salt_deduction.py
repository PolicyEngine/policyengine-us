from policyengine_us.model_api import *


class mt_salt_deduction(Variable):
    value_type = float
    entity = Person
    label = "Montana state and local tax deduction"
    unit = USD
    definition_period = YEAR
    documentation = (
        "State and local taxes on a return with one column: a single, head "
        "of household or joint return, or a married person filing on a "
        "separate form. For 2018-2023 the filer deducts real estate taxes "
        "plus the larger of sales taxes and local income taxes (Itemized "
        "Deductions Schedule line 5, with the election in 26 USC "
        "164(b)(5)(A)), up to $10,000 ($5,000 for a married person filing "
        "separately). For 2017 the filer deducts the same taxes with no cap, "
        "and 2015 and 2016 take the 2017 rules. Through 2023 the tax unit "
        "head receives the return's total."
    )
    reference = (
        "https://revenuefiles.mt.gov/files/forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2017_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=29",
        # PDF pages 27-28
        "https://revenuefiles.mt.gov/files/forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2018_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=27",
        # PDF pages 32-33
        "https://revenuefiles.mt.gov/files/forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2019_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=32",
        # PDF pages 29-30
        "https://revenuefiles.mt.gov/files/forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2020_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=29",
        "https://revenuefiles.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2/2021_Montana_Individual_Income_Tax_Return_Form_2.pdf#page=7",
        "https://revenuefiles.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2/2022_Montana_Individual_Income_Tax_Return_Form_2.pdf#page=7",
        "https://revenuefiles.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2/2023_Montana_Individual_Income_Tax_Return_Form_2.pdf#page=7",
        "https://revenuefiles.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2021_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=32",
        "https://revenuefiles.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2022_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=34",
        "https://revenuefiles.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2023_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=37",
        "https://mca.legmt.gov/bills/2017/mca/title_0150/chapter_0300/part_0210/section_0310/0150-0300-0210-0310.html",
        "https://mca.legmt.gov/bills/2019/mca/title_0150/chapter_0300/part_0210/section_0310/0150-0300-0210-0310.html",
        "https://mca.legmt.gov/bills/2022/mca/title_0150/chapter_0300/part_0210/section_0310/0150-0300-0210-0310.html",
        "https://www.govinfo.gov/content/pkg/USCODE-2023-title26/html/USCODE-2023-title26-subtitleA-chap1-subchapB-partVI-sec164.htm",
        # Former MCA 15-30-2131(1)(a)(ii) (MCA 2017, 2019 and 2021): items
        # under IRC 161, except state income tax paid. Congress capped the
        # deduction for tax years after 2017 under 26 USC 164(b)(6).
    )
    defined_for = StateCode.MT

    def formula(person, period, parameters):
        p = parameters(period).gov.irs.deductions.itemized.salt_and_real_estate
        p_mt = parameters(period).gov.states.mt.tax.income.deductions.itemized
        filing_status = person.tax_unit("filing_status", period)
        cap = p.cap[filing_status]
        if p_mt.state_specific_deduction_applies:
            # Taxpayers elect sales taxes or local income taxes under IRC
            # 164(b)(5)(A), then add real estate taxes before applying the cap.
            # Congress set no cap before 2018, so a 2017 return deducts the
            # full amount.
            sales_tax = add(
                person.tax_unit, period, ["state_sales_tax", "local_sales_tax"]
            )
            # We read the tax unit's local_income_tax for the joint return.
            # For each separate column, mt_salt_deduction_indiv reads that
            # spouse's own Kansas City, St. Louis and Philadelphia taxes plus
            # spouse_allocation_rate (half) of the remaining
            # local_income_tax, floored at zero. If a user sets
            # local_income_tax below the sum of those city taxes, the two
            # paths receive different amounts.
            local_income_tax = person.tax_unit("local_income_tax", period)
            real_estate_tax = add(person.tax_unit, period, ["real_estate_taxes"])
            taxes = real_estate_tax + max_(sales_tax, local_income_tax)
            is_head = person("is_tax_unit_head", period)
            return is_head * min_(taxes, cap)
        # Preserve the per-person real estate deduction from 2024.
        real_estate_tax = person("real_estate_taxes", period)
        return min_(real_estate_tax, cap)
