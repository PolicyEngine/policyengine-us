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
        age_over_65_qualifies = age >= p.min_age

        ssi = person("ssi", period)
        ssi_qualifies = ssi > 0
        age_under_65_qualifies = ~age_over_65_qualifies & ssi_qualifies

        property_tax = person("real_estate_taxes", period)
        rent = person("rent", period)
        payment_qualifies = (property_tax + rent) > 0

        head = person("is_tax_unit_head", period)

        return tax_unit.any(
            head
            & (age_over_65_qualifies | age_under_65_qualifies)
            & payment_qualifies
        )
