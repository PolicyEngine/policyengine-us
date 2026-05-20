from policyengine_us.model_api import *


HALF_COUNTED_BENEFIT_SOURCES = [
    "social_security",
    "ssi_reported",
    "railroad_benefits",
]

TAX_EXEMPT_INCOME_SOURCES = [
    "tax_exempt_interest_income",
    "tax_exempt_pension_income",
    "tax_exempt_retirement_distributions",
]


class pa_property_tax_or_rent_rebate_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Pennsylvania Property Tax/Rent Rebate income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.pa.gov/content/dam/copapwp-pagov/en/revenue/documents/"
        "formsandpublications/formsforindividuals/ptrr/documents/"
        "2025_pa-1000_inst.pdf#page=6"
    )
    defined_for = StateCode.PA

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.pa.tax.property.property_tax_or_rent_rebate
        person = tax_unit.members
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        adjusted_gross_income = tax_unit("adjusted_gross_income", period)
        above_the_line_deductions = tax_unit("above_the_line_deductions", period)
        taxable_social_security = tax_unit("tax_unit_taxable_social_security", period)
        half_counted_benefits = tax_unit.sum(
            head_or_spouse * add(person, period, HALF_COUNTED_BENEFIT_SOURCES)
        )
        tax_exempt_income = tax_unit.sum(
            head_or_spouse * add(person, period, TAX_EXEMPT_INCOME_SOURCES)
        )
        csrs_income = tax_unit.sum(
            head_or_spouse * person("csrs_retirement_pay", period)
        )
        csrs_recipients = tax_unit.sum(
            head_or_spouse & (person("csrs_retirement_pay", period) > 0)
        )
        csrs_exclusion = min_(csrs_income, csrs_recipients * p.csrs_income_exclusion)

        return max_(
            0,
            adjusted_gross_income
            + above_the_line_deductions
            - taxable_social_security
            + p.benefit_income_rate * half_counted_benefits
            + tax_exempt_income
            + csrs_income
            - csrs_exclusion,
        )
