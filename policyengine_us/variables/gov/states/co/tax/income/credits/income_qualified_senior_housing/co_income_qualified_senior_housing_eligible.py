from policyengine_us.model_api import *


class co_income_qualified_senior_housing_credit_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for Colorado Income Qualified Senior Housing Income Tax Credit"
    definition_period = YEAR
    reference = (
        "https://tax.colorado.gov/income-qualified-senior-housing-income-tax-credit",
        "https://tax.colorado.gov/sites/tax/files/documents/DR_104_Book_2022.pdf#page=17",
    )
    defined_for = StateCode.CO

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.co.tax.income.credits.income_qualified_senior_housing

        age_head = tax_unit("age_head", period)
        age_spouse = tax_unit("age_spouse", period)

        head_eligible = age_head >= p.age_limit
        spouse_eligible = age_spouse >= p.age_limit
        age_eligible = head_eligible | spouse_eligible

        agi = tax_unit("adjusted_gross_income", period)
        max_income = p.income_threshold
        agi_eligible = agi <= max_income

        property_tax_exemption_claimed = (
            tax_unit("co_property_tax_exemption", period) > 0
        )

        return age_eligible & agi_eligible & ~property_tax_exemption_claimed
