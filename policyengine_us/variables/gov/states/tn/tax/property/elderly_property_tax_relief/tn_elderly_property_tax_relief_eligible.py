from policyengine_us.model_api import *


class tn_elderly_property_tax_relief_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Tennessee elderly property tax relief"
    definition_period = YEAR
    reference = (
        "https://comptroller.tn.gov/office-functions/pa/property-taxes/property-tax-programs/tax-relief.html",
        "https://comptroller.tn.gov/content/dam/cot/pa/documents/tax-relief/TaxReliefBrochure.pdf#page=2",
        "https://comptroller.tn.gov/content/dam/cot/pa/documents/tax-relief/TCA%2067-5-701%20through%2067-5-704.pdf#page=3",
    )
    defined_for = StateCode.TN

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.tn.tax.property.elderly_property_tax_relief
        person = tax_unit.members
        head = person("is_tax_unit_head", period)
        joint_spouse = person("is_tax_unit_spouse", period) & person.tax_unit(
            "tax_unit_is_joint", period
        )
        head_or_joint_spouse = head | joint_spouse
        age = person("age", period.this_year)
        assessed_property_value = tax_unit.sum(
            person("assessed_property_value", period) * head_or_joint_spouse
        )
        real_estate_taxes = tax_unit.sum(
            person("real_estate_taxes", period) * head_or_joint_spouse
        )
        return (
            tax_unit.any((age >= p.age_threshold) & head_or_joint_spouse)
            & (
                tax_unit("tn_elderly_property_tax_relief_income", period)
                <= p.income_limit
            )
            & (real_estate_taxes > 0)
            & (assessed_property_value > 0)
            & ~tax_unit("rents", period)
        )
