from policyengine_us.model_api import *


class az_property_tax_credit_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Arizona Property Tax Credit"
    definition_period = YEAR
    reference = "https://www.azleg.gov/viewdocument/?docName=https://www.azleg.gov/ars/43/01072.htm"
    defined_for = StateCode.AZ

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        p = parameters(period).gov.states.az.tax.income.credits.property_tax

        head_or_spouse = person("is_tax_unit_head_or_spouse", period)

        age = person("age", period)
        age_eligible_head_or_spouse = (age >= p.age_threshold) & head_or_spouse

        receives_ssi = person("ssi", period) > 0
        head_or_spouse_receives_ssi = (receives_ssi > 0) & head_or_spouse

        age_or_ssi_eligible = tax_unit.any(
            age_eligible_head_or_spouse | head_or_spouse_receives_ssi
        )

        paid_rent_or_property_tax = (
            add(tax_unit, period, ["rent", "real_estate_taxes"]) > 0
        )

        return age_or_ssi_eligible & paid_rent_or_property_tax
