from policyengine_us.model_api import *


class ca_itemized_deductions_pre_limitation(Variable):
    value_type = float
    entity = TaxUnit
    label = "California pre-limitation itemized deductions"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.ftb.ca.gov/forms/2021/2021-540-ca-instructions.html",
        "https://www.ftb.ca.gov/forms/2022/2022-540-ca-instructions.html",
        # Schedule CA (540) Part II line 16, claim of right
        "https://www.ftb.ca.gov/forms/2025/2025-540-ca-instructions.html",
        "https://www.ftb.ca.gov/about-ftb/data-reports-plans/summary-of-federal-income-tax-changes/index.html",
        # 2024 Schedule CA (540) instructions, line 15
        "https://www.ftb.ca.gov/forms/2024/2024-540-booklet.pdf#page=66",
    )
    defined_for = StateCode.CA

    def formula(tax_unit, period, parameters):
        # Exclude the replaced federal amounts before summation, so changes
        # to federal charity/misc/casualty rules cannot cause cancellation
        # errors. Schedule CA line 15 replaces the federal casualty loss,
        # which is limited to declared disasters from 2018, with California's
        # own.
        # Schedule CA Part II line 16, column A, carries the federal claim
        # of right deduction by default. Not modeled: California's own credit
        # and column B removal (Form 540 line 78, "IRC 1341"), the column C
        # deduction when federal tax used the credit, and the bar for income
        # California did not tax, including Social Security repayments.
        federal_components = parameters(period).gov.irs.deductions.itemized_deductions
        deductions = [
            variable
            for variable in federal_components
            if variable
            not in (
                "salt_deduction",
                "charitable_deduction",
                "charitable_deduction_for_non_itemizers",
                "misc_deduction",
                "casualty_loss_deduction",
            )
        ]
        deductions += [
            "ca_investment_interest_expense_deduction",
            "real_estate_taxes",
            "ca_charitable_deduction",
            "ca_misc_deduction",
            "ca_casualty_loss_deduction",
        ]
        # Federal investment interest and mortgage insurance premiums are
        # nested in interest_deduction. California disallows the premiums
        # (Schedule CA line 8d), including when federal law restores them.
        return add(tax_unit, period, deductions) - add(
            tax_unit,
            period,
            [
                "investment_interest_expense",
                "deductible_mortgage_insurance_premiums",
            ],
        )
