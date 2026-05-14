from policyengine_us.model_api import *


class in_over_65_property_tax_credit_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Indiana Over 65 Property Tax Credit"
    definition_period = YEAR
    reference = "https://www.in.gov/counties/monroe/Departments/auditor/over-65/"
    defined_for = StateCode.IN

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states["in"].tax.property.over_65_credit
        filing_status = tax_unit("filing_status", period)
        status = filing_status.possible_values
        person = tax_unit.members
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        age = person("age", period.this_year)

        senior = tax_unit.any(
            (age >= p.age_threshold) & head_or_spouse,
        )
        surviving_spouse = (filing_status == status.SURVIVING_SPOUSE) & (
            tax_unit.any(
                (age >= p.surviving_spouse_age_threshold) & head_or_spouse,
            )
        )
        income_eligible = (
            tax_unit("adjusted_gross_income", period) <= p.income_limit[filing_status]
        )
        homeowner = add(tax_unit, period, ["real_estate_taxes"]) > 0

        return (senior | surviving_spouse) & income_eligible & homeowner
