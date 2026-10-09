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
        "https://www.ftb.ca.gov/forms/2025/2025-540-ca-instructions.html",
        "https://www.ftb.ca.gov/about-ftb/data-reports-plans/summary-of-federal-income-tax-changes/index.html",
    )
    defined_for = StateCode.CA

    def formula(tax_unit, period, parameters):
        # Exclude the replaced federal amounts before summation, so changes
        # to federal charity/misc rules cannot cause cancellation errors.
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
            )
        ]
        deductions += [
            "ca_investment_interest_expense_deduction",
            "real_estate_taxes",
            "ca_charitable_deduction",
            "ca_misc_deduction",
        ]
        # Federal investment interest is nested in interest_deduction.
        return add(tax_unit, period, deductions) - add(
            tax_unit, period, ["investment_interest_expense"]
        )
