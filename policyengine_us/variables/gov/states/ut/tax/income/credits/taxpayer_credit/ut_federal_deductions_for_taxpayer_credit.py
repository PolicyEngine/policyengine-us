from policyengine_us.model_api import *


class ut_federal_deductions_for_taxpayer_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Utah federal deductions considered for taxpayer credit"
    unit = USD
    documentation = (
        "Federal deductions added to the Utah personal exemption for the taxpayer "
        "credit. Income-tax electors subtract paid and reported income tax up to "
        "$10,000 for 2018 through 2025; before 2018 and from 2026 they subtract "
        "only the federally allowed income-tax share."
    )
    definition_period = YEAR
    defined_for = StateCode.UT
    reference = (
        # Utah Code 59-10-1018(2)(a)(ii)(A), the edition superseded on May 8,
        # 2018: the federal itemized deduction less the state or local income
        # taxes deducted as an itemized deduction.
        "https://le.utah.gov/xcode/Title59/Chapter10/C59-10-S1018_1800010118000101.html",
        # Utah Code 59-10-1018(1)(e) and (1)(f)(i), 2023 edition: only state
        # or local income tax is removed from the federal itemized total. The
        # 2021 edition reads the same, and the edition effective May 8, 2018
        # has the text at (1)(g) and (1)(h)(i).
        "https://le.utah.gov/xcode/Title59/Chapter10/C59-10-S1018_2023050320230503.html",
        # Utah Code 59-10-1018(1)(e) and (1)(f)(i), the edition for tax years
        # from 2026.
        "https://le.utah.gov/xcode/Title59/Chapter10/C59-10-S1018_2026050620260506.pdf#page=1",
        # H.B. 77 section 29 applies the 2026 amendment from January 1.
        "https://le.utah.gov/Session/2026/bills/enrolled/HB0077.pdf#page=138",
        # 2017 TC-40 line 14 worksheet prorates income tax after section 68.
        "https://files.tax.utah.gov/tax/forms/2017/tc-40inst.pdf#page=11",
        # 2025 TC-40 instructions, line 14: do not remove itemized sales tax.
        "https://files.tax.utah.gov/tax/forms/2025/tc-40inst.pdf#page=10",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.irs.deductions
        p_ut = parameters(
            period
        ).gov.states.ut.tax.income.credits.taxpayer.income_tax_removal
        us_itemizing = tax_unit("tax_unit_itemizes", period)
        std_ded = tax_unit("standard_deduction", period)
        itemized = tax_unit("itemized_taxable_income_deductions", period)
        salt_deduction = tax_unit("salt_deduction", period)
        raw_state_income_or_sales_tax = tax_unit(
            "state_and_local_sales_or_income_tax", period
        )
        income_tax = add(
            tax_unit, period, ["state_withheld_income_tax", "local_income_tax"]
        )
        sales_tax = add(tax_unit, period, ["state_sales_tax", "local_sales_tax"])
        # Sales-tax election only where the SALT amount the federal side used
        # equals the sales tax and not the income tax, whether the formula
        # (the larger of the two) or an input supplied it. A tie or a supplied
        # amount that matches neither keeps the income-tax treatment.
        sales_tax_elected = np.isclose(
            raw_state_income_or_sales_tax, sales_tax
        ) & ~np.isclose(raw_state_income_or_sales_tax, income_tax)
        deductions = [
            deduction
            for deduction in p.itemized_deductions
            if deduction != "salt_deduction"
        ]
        fallback_itemized = add(tax_unit, period, deductions)
        real_estate_tax = add(tax_unit, period, ["real_estate_taxes"])
        reconstructed_itemized = fallback_itemized + salt_deduction
        # A positive federal total includes section 68's reduction. Preserve
        # the existing reconstruction when the total is zero.
        effective_itemized = where(itemized > 0, itemized, reconstructed_itemized)

        # Claimants subtract paid and reported income tax up to $10,000
        # under 59-10-1018(1)(e) for 2018 through 2025, even above SALT limits.
        income_tax_to_remove = min_(raw_state_income_or_sales_tax, p_ut.cap)
        if p_ut.deducted_only:
            # Allocate property tax within the actual federal SALT deduction,
            # which already reflects salt_cap and its income phase-down.
            deducted_income_tax = max_(salt_deduction - real_estate_tax, 0)
            limitation = p.itemized.limitation
            excluded_deductions = 0
            if not limitation.obbb.applies:
                excluded_deductions = add(
                    tax_unit, period, limitation.excluded_deductions
                )
            # Filers prorate income tax after section 68 under the 2017
            # line 14 worksheet. From 2026 all deductions share the reduction.
            limited_deductions = max_(reconstructed_itemized - excluded_deductions, 0)
            retained_fraction = np.divide(
                max_(effective_itemized - excluded_deductions, 0),
                limited_deductions,
                out=np.ones_like(effective_itemized),
                where=limited_deductions > 0,
            )
            retained_fraction = min_(retained_fraction, 1)
            income_tax_to_remove = min_(
                income_tax_to_remove, deducted_income_tax * retained_fraction
            )
            income_tax_to_remove = min_(income_tax_to_remove, effective_itemized)

        # Keep the signed difference: personal exemptions enter the credit
        # before its final zero floor. Sales-tax electors subtract nothing.
        itemized_base = effective_itemized - where(
            sales_tax_elected, 0, income_tax_to_remove
        )
        return where(us_itemizing, itemized_base, std_ded)
