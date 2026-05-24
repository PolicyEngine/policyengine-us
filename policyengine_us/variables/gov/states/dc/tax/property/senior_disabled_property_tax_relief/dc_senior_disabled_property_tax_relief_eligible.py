from policyengine_us.model_api import *


class dc_senior_disabled_property_tax_relief_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the DC senior disabled property tax relief"
    definition_period = YEAR
    reference = (
        "https://otr.cfo.dc.gov/page/real-property-tax-reliefs-credits-and-deductions",
        "https://code.dccouncil.gov/us/dc/council/code/sections/47-863",
    )
    defined_for = StateCode.DC

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.dc.tax.property.senior_disabled_property_tax_relief
        age_eligible = tax_unit("greater_age_head_spouse", period) >= p.age_threshold
        person = tax_unit.members
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        disabled = person("is_permanently_and_totally_disabled", period) | (
            add(
                person,
                period,
                ["ssi", "social_security_disability", "total_disability_payments"],
            )
            > 0
        )
        disability_eligible = tax_unit.any(head_or_spouse & disabled)
        income = tax_unit.spm_unit(
            "dc_senior_disabled_property_tax_relief_income", period
        )
        income_eligible = income < p.income_limit
        pays_property_taxes = add(tax_unit, period, ["real_estate_taxes"]) > 0
        is_renter = tax_unit("rents", period)
        return (
            (age_eligible | disability_eligible)
            & income_eligible
            & pays_property_taxes
            & ~is_renter
        )
