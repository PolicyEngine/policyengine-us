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
        "https://revenuefiles.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2023_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=12",
        # 2023 instructions, "How to allocate income and deductions when
        # filing separately": "each column constituting its own return".
        "https://revenuefiles.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2023_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=37",
        "https://mca.legmt.gov/bills/2022/mca/title_0150/chapter_0300/part_0210/section_0310/0150-0300-0210-0310.html",
        # Former MCA 15-30-2131(1)(a)(ii) (2021). The cap is 26 USC 164(b)(6).
    )
    defined_for = "mt_married_filing_separately_on_same_return_eligible"

    def formula(person, period, parameters):
        p = parameters(period).gov.irs.deductions.itemized.salt_and_real_estate
        p_mt = parameters(period).gov.states.mt.tax.income.deductions.itemized
        filing_status = person.tax_unit("filing_status", period)
        # A married couple's columns are each "married filing separately":
        # "not more than ... $5,000 if you are married filing separately".
        # Other filers have one column at their own status's cap.
        married = filing_status == filing_status.possible_values.JOINT
        cap = where(married, p.cap.SEPARATE, p.cap[filing_status])
        # Line 5c: each spouse's own real estate taxes.
        real_estate_tax = person("real_estate_taxes", period)
        # Line 5a: PolicyEngine estimates sales taxes for the tax unit only.
        # Jointly paid expenses "can be allocated to either spouse in any
        # proportional amount", so a couple divides them equally.
        sales_tax = add(person.tax_unit, period, ["state_sales_tax", "local_sales_tax"])
        sales_tax_share = where(married, p_mt.spouse_allocation_rate, 1)
        # Line 5b: "Deductions that are attributable to only one spouse must
        # be claimed by that spouse." PolicyEngine computes local income
        # taxes for the tax unit. The ones it levies on a Montana household
        # are city taxes on earnings there (Kansas City, St. Louis,
        # Philadelphia), so each person takes a share in proportion to their
        # own earnings taxed by those cities. Without such earnings the tax
        # is divided like the sales taxes.
        local_base = add(
            person,
            period,
            [
                "mo_kansas_city_earnings_tax_taxable_earnings",
                "mo_st_louis_earnings_tax_taxable_earnings",
                "pa_philadelphia_wage_tax_taxable_wages",
            ],
        )
        unit_local_base = person.tax_unit.sum(local_base)
        has_local_base = unit_local_base > 0
        local_share = where(
            has_local_base,
            local_base / where(has_local_base, unit_local_base, 1),
            sales_tax_share,
        )
        local_income_tax = person.tax_unit("local_income_tax", period)
        taxes = (
            real_estate_tax
            + sales_tax_share * sales_tax
            + local_share * local_income_tax
        )
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        return head_or_spouse * min_(taxes, cap)
