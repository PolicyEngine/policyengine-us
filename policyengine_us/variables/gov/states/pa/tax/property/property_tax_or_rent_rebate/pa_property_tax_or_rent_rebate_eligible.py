from policyengine_us.model_api import *


class pa_property_tax_or_rent_rebate_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Pennsylvania Property Tax/Rent Rebate"
    definition_period = YEAR
    reference = "https://www.pa.gov/agencies/revenue/ptrr"
    defined_for = StateCode.PA

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.pa.tax.property.property_tax_or_rent_rebate
        filing_status = tax_unit("filing_status", period)
        person = tax_unit.members
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        age = person("age", period.this_year)
        is_disabled = person("is_disabled", period)
        age_eligible = tax_unit.any((age >= p.age_threshold) & head_or_spouse)
        widow_eligible = (
            filing_status == filing_status.possible_values.SURVIVING_SPOUSE
        ) & tax_unit.any(
            (age >= p.widow_age_threshold) & head_or_spouse,
        )
        disabled_eligible = tax_unit.any(
            (age >= p.disability_age_threshold) & is_disabled & head_or_spouse,
        )

        return (
            (age_eligible | widow_eligible | disabled_eligible)
            & (tax_unit("adjusted_gross_income", period) <= p.income_limit)
            & (add(tax_unit, period, ["rent", "real_estate_taxes"]) > 0)
        )
