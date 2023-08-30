from policyengine_us.model_api import *


class co_sales_tax_refund_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Colorado sales tax refund"
    definition_period = YEAR
    reference = "https://tax.colorado.gov/sites/tax/files/documents/DR_0104_Book_2022.pdf#page=23"
    defined_for = StateCode.CO

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.co.tax.income.credits.sales_tax_refund
        age_head = tax_unit("age_head", period)
        head_eligible = age_head >= p.age_threshold
        age_spouse = tax_unit("age_spouse", period)
        spouse_eligible = age_spouse >= p.age_threshold
        # Legal code is ambiguous, but the form points to the line corresponding to
        # tax before non-refundable credits.
        income_tax_eligible = (
            tax_unit("co_income_tax_before_non_refundable_credits", period) > 0
        )
        employment_income_eligible = (
            add(tax_unit, period, ["employment_income"]) > 0
        )
        income_eligible = employment_income_eligible | income_tax_eligible
        age_eligible = head_eligible | spouse_eligible
        return age_eligible | income_eligible
