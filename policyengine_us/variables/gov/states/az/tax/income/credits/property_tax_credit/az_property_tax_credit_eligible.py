from policyengine_us.model_api import *


class az_property_tax_credit_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Arizona Property Tax Credit"
    definition_period = YEAR
    defined_for = StateCode.AZ

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        p = parameters(period).gov.states.az.tax.income.credits.property_tax

        age = person("age", period)
        age_eligible = age >= p.age_threshold

        ssi = person("ssi", period)
        ssi_eligible = ssi > 0
        age_or_ssi_eligible = tax_unit.any(age_eligible | ssi_eligible)

        property_tax = add(tax_unit, period, ["real_estate_taxes"])
        rent = add(tax_unit, period, ["rent"])
        payment_eligible = (property_tax + rent) > 0

        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        head_or_spouse_in_tax_unit = tax_unit.any(is_head_or_spouse)

        return (
            head_or_spouse_in_tax_unit & age_or_ssi_eligible & payment_eligible
        )
