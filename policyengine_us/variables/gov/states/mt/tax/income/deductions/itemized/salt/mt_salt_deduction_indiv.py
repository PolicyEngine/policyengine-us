from policyengine_us.model_api import *


class mt_salt_deduction_indiv(Variable):
    value_type = float
    entity = Person
    label = "Montana state and local tax deduction when married couples are filing separately"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Itemized Deductions Schedule, line 5, in each spouse's column when "
        "a married couple files separately on the same form (filing status "
        "2a). Each column is a separate return, capped at the married filing "
        "separately amount."
    )
    reference = (
        "https://revenuefiles.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2/2021_Montana_Individual_Income_Tax_Return_Form_2.pdf#page=7",
        "https://revenuefiles.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2/2022_Montana_Individual_Income_Tax_Return_Form_2.pdf#page=7",
        "https://revenuefiles.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2/2023_Montana_Individual_Income_Tax_Return_Form_2.pdf#page=7",
        # PDF pages 10, 32
        "https://revenuefiles.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2021_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=10",
        # PDF pages 11, 34
        "https://revenuefiles.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2022_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=11",
        # PDF pages 12-13, 37
        "https://revenuefiles.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2023_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=12",
        # PDF pages 3-4
        "https://www.irs.gov/pub/irs-prior/i1040sca--2023.pdf#page=3",
        "https://www.govinfo.gov/content/pkg/USCODE-2023-title26/html/USCODE-2023-title26-subtitleA-chap1-subchapB-partVI-sec164.htm",
        "https://mca.legmt.gov/bills/2022/mca/title_0150/chapter_0300/part_0210/section_0310/0150-0300-0210-0310.html",
        # Former MCA 15-30-2131(1)(a)(ii) (2021). The cap is 26 USC 164(b)(6).
    )
    defined_for = "mt_married_filing_separately_on_same_return_eligible"

    def formula(person, period, parameters):
        p = parameters(period).gov.irs.deductions.itemized.salt_and_real_estate
        p_mt = parameters(period).gov.states.mt.tax.income.deductions.itemized
        filing_status = person.tax_unit("filing_status", period)
        column_status = person.tax_unit(
            "state_filing_status_if_married_filing_separately_on_same_return", period
        )
        cap = p.cap[column_status]
        married = filing_status == filing_status.possible_values.JOINT
        real_estate_tax = person("real_estate_taxes", period)
        # Tax-unit sales taxes lack an owner. Allocate half to each spouse.
        sales_tax = add(person.tax_unit, period, ["state_sales_tax", "local_sales_tax"])
        sales_tax_share = where(married, p_mt.spouse_allocation_rate, 1)
        # Each spouse claims the city income taxes on their own earnings.
        # Split residual tax-unit local income taxes equally as a convention
        # when the input does not identify who paid them.
        own_local_tax = add(
            person,
            period,
            [
                "mo_kansas_city_earnings_tax_person",
                "mo_st_louis_earnings_tax_person",
                "pa_philadelphia_wage_tax_person",
            ],
        )
        local_income_tax = person.tax_unit("local_income_tax", period)
        other_local_tax = max_(0, local_income_tax - person.tax_unit.sum(own_local_tax))
        # Each column elects its own larger category under IRC 164(b)(5)(A).
        income_tax = own_local_tax + sales_tax_share * other_local_tax
        taxes = real_estate_tax + max_(sales_tax_share * sales_tax, income_tax)
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        return head_or_spouse * min_(taxes, cap)
