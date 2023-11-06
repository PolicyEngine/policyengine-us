from policyengine_us.model_api import *


class de_itemized_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Delaware itemized deductions"
    unit = USD
    definition_period = YEAR
    reference = "https://revenuefiles.delaware.gov/2022/TY22_PIT-RSA_2022-02_PaperInteractive.pdf"
    defined_for = StateCode.DE

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.irs.deductions
        filing_status = tax_unit("filing_status", period)
        deductions = [
            deduction
            for deduction in p.itemized_deductions
            if deduction not in ["interest_deduction", "salt_deduction"]
        ]
        federal_deductions = add(tax_unit, period, deductions)

        salt_sales_or_income = tax_unit(
            "state_and_local_sales_or_income_tax", period
        )

        total_salt = (
            add(tax_unit, period, ["real_estate_taxes"]) + salt_sales_or_income
        )

        salt_amount = min_(
            total_salt, p.itemized.salt_and_real_estate.cap[filing_status]
        )

        interest = add(
            tax_unit,
            period,
            ["mortgage_interest", "investment_income_form_4952"],
        )

        return federal_deductions + salt_amount + interest
