from policyengine_us.model_api import *


class pa_property_tax_or_rent_rebate_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Pennsylvania Property Tax/Rent Rebate income"
    unit = USD
    definition_period = YEAR
    reference = "https://www.pa.gov/content/dam/copapwp-pagov/en/revenue/documents/formsandpublications/formsforindividuals/ptrr/documents/2025_pa-1000_inst.pdf"
    defined_for = StateCode.PA

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.pa.tax.property.property_tax_or_rent_rebate
        adjusted_gross_income = tax_unit("adjusted_gross_income", period)
        above_the_line_deductions = tax_unit("above_the_line_deductions", period)
        taxable_social_security = tax_unit("tax_unit_taxable_social_security", period)
        half_counted_benefits = add(
            tax_unit,
            period,
            [
                "social_security",
                "ssi_reported",
                "railroad_benefits",
            ],
        )
        tax_exempt_income = add(
            tax_unit,
            period,
            [
                "tax_exempt_interest_income",
                "tax_exempt_pension_income",
                "tax_exempt_retirement_distributions",
            ],
        )

        return max_(
            0,
            adjusted_gross_income
            + above_the_line_deductions
            - taxable_social_security
            + p.benefit_income_rate * half_counted_benefits
            + tax_exempt_income,
        )
