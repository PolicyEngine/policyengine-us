from policyengine_us.model_api import *


class in_over_65_property_tax_credit_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Indiana Over 65 Property Tax Credit"
    definition_period = YEAR
    reference = (
        "https://www.in.gov/counties/monroe/Departments/auditor/over-65/",
        "https://www.in.gov/dlgf/files/2025-memos/250612-Cockerill-Memo-Legislation-Affecting-Deductions%2C-Exemptions%2C-and-Credits.pdf#page=2",
    )
    defined_for = StateCode.IN

    def formula(tax_unit, period, parameters):
        prior_prior_year = period.offset(-2, "year")
        p = parameters(period).gov.states["in"].tax.property.over_65_credit
        income_year_filing_status = tax_unit("filing_status", prior_prior_year)
        current_filing_status = tax_unit("filing_status", period)
        status = current_filing_status.possible_values
        person = tax_unit.members
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        age = person("age", period.this_year)
        is_surviving_spouse = person("is_surviving_spouse", period)

        senior = tax_unit.any(
            (age >= p.age_threshold) & head_or_spouse,
        )
        marked_surviving_spouse = tax_unit.any(
            (age >= p.surviving_spouse_age_threshold)
            & is_surviving_spouse
            & head_or_spouse,
        )
        federal_surviving_spouse = (
            current_filing_status == status.SURVIVING_SPOUSE
        ) & tax_unit.any(
            (age >= p.surviving_spouse_age_threshold) & head_or_spouse,
        )
        surviving_spouse = marked_surviving_spouse | federal_surviving_spouse
        income_eligible = (
            tax_unit("adjusted_gross_income", prior_prior_year)
            <= p.income_limit[income_year_filing_status]
        )
        homeowner = add(tax_unit, period, ["real_estate_taxes"]) > 0

        return (senior | surviving_spouse) & income_eligible & homeowner
