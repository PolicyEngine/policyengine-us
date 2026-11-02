from policyengine_us.model_api import *


class ut_federal_deductions_for_taxpayer_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Utah federal deductions considered for taxpayer credit"
    unit = USD
    documentation = "These federal deductions are added to the Utah personal exemption to determine the Utah taxpayer credit."
    definition_period = YEAR
    defined_for = StateCode.UT
    reference = (
        "https://le.utah.gov/xcode/Title59/Chapter10/59-10-S114.html?v=C59-10-S114_2022032320220323",
        # Utah Code 59-10-1018(1)(f)(i): only state or local income tax is
        # removed from the federal itemized total.
        "https://le.utah.gov/xcode/Title59/Chapter10/C59-10-S1018_2026050620260506.pdf#page=1",
        # 2025 TC-40 instructions, line 14: do not remove itemized sales tax.
        "https://files.tax.utah.gov/tax/forms/2025/tc-40inst.pdf#page=10",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.irs.deductions
        filing_status = tax_unit("filing_status", period)
        us_itemizing = tax_unit("tax_unit_itemizes", period)
        std_ded = tax_unit("standard_deduction", period)
        itemized = tax_unit("itemized_taxable_income_deductions", period)
        salt_deduction = tax_unit("salt_deduction", period)
        raw_state_income_or_sales_tax = tax_unit(
            "state_and_local_sales_or_income_tax", period
        )
        # state_and_local_sales_or_income_tax takes the larger of income and
        # sales taxes, so a strictly larger sales amount is a sales election.
        income_tax = add(
            tax_unit, period, ["state_withheld_income_tax", "local_income_tax"]
        )
        sales_tax = add(tax_unit, period, ["state_sales_tax", "local_sales_tax"])
        sales_tax_elected = sales_tax > income_tax
        deductions = [
            deduction
            for deduction in p.itemized_deductions
            if deduction != "salt_deduction"
        ]
        fallback_itemized = add(tax_unit, period, deductions)
        real_estate_tax = add(tax_unit, period, ["real_estate_taxes"])
        capped_real_estate_tax = min_(
            real_estate_tax, p.itemized.salt_and_real_estate.cap[filing_status]
        )
        deducted_state_income_or_sales_tax = max_(
            salt_deduction - capped_real_estate_tax, 0
        )
        # Income-tax election: remove the income tax, keep real-estate taxes.
        income_fallback_base = fallback_itemized + capped_real_estate_tax
        explicit_itemized_override = itemized > income_fallback_base
        claimed_state_income_tax = where(
            salt_deduction > 0,
            deducted_state_income_or_sales_tax,
            where(explicit_itemized_override, raw_state_income_or_sales_tax, 0),
        )
        income_claimed_base = max_(
            itemized - claimed_state_income_tax, income_fallback_base
        )
        # Sales-tax election: 59-10-1018(1)(f)(i) removes no sales tax, so
        # the whole allowed SALT deduction stays in the base.
        sales_fallback_base = fallback_itemized + salt_deduction
        sales_claimed_base = max_(itemized, sales_fallback_base)
        fallback_base = where(
            sales_tax_elected, sales_fallback_base, income_fallback_base
        )
        claimed_base = where(sales_tax_elected, sales_claimed_base, income_claimed_base)
        itemized_base = where(itemized > 0, claimed_base, fallback_base)
        return where(
            us_itemizing,
            itemized_base,
            std_ded,
        )
