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
    )
    defined_for = StateCode.CA

    def formula(tax_unit, period, parameters):
        deductions = add(
            tax_unit,
            period,
            [
                "itemized_deductions_less_salt",
                "ca_investment_interest_expense_deduction",
                "real_estate_taxes",
            ],
        )
        # Remove the federal investment interest that
        # itemized_deductions_less_salt includes through interest_deduction,
        # which counts only the head's and spouse's own interest.
        federal_investment_interest = tax_unit_non_dep_add(
            tax_unit, period, ["investment_interest_expense"]
        )
        return deductions - federal_investment_interest
