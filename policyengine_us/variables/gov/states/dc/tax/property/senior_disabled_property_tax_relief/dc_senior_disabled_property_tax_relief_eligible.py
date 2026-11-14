from policyengine_us.model_api import *


class dc_senior_disabled_property_tax_relief_eligible(Variable):
    """Eligibility given known reference-year income and explicit property facts.

    Missing required facts suppress an estimate; they do not establish legal
    ineligibility. From 2025 the same resident must qualify by age or disability
    and personally hold the required ownership interest.
    """

    value_type = bool
    entity = TaxUnit
    label = "Eligible for the DC senior disabled property tax relief"
    definition_period = YEAR
    reference = (
        "https://otr.cfo.dc.gov/page/real-property-tax-reliefs-credits-and-deductions",
        "https://code.dccouncil.gov/us/dc/council/code/sections/47-863",
        "https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/ASD%20100%20Instructions.pdf#page=1",
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

    def formula_2025(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.dc.tax.property.senior_disabled_property_tax_relief
        person = tax_unit.members
        share = person("dc_senior_disabled_property_tax_relief_ownership_share", period)
        category_eligible = (person("age", period) >= p.age_threshold) | person(
            "dc_senior_disabled_property_tax_relief_qualifying_disability", period
        )
        owner_eligible = tax_unit.any(
            category_eligible & (share >= p.ownership_share_threshold) & (share <= 1)
        )
        income_available = tax_unit.household(
            "dc_senior_disabled_property_tax_relief_household_prior_agi_available",
            period,
        )
        residence_eligible = tax_unit.household(
            "dc_senior_disabled_property_tax_relief_residence_eligible", period
        )
        income = tax_unit.spm_unit(
            "dc_senior_disabled_property_tax_relief_income", period
        )
        tax = tax_unit("dc_senior_disabled_property_tax_relief_pre_relief_tax", period)
        return (
            owner_eligible
            & income_available
            & residence_eligible
            & (income < p.income_limit)
            & (tax > 0)
        )
