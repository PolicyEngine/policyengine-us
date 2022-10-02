from openfisca_us.model_api import *


class mo_property_tax_credit_demographic_tests(Variable):
    value_type = float
    entity = TaxUnit
    label = "MO property tax credit demographic eligiblity test"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://dor.mo.gov/forms/MO-PTS_2021.pdf",
        "https://revisor.mo.gov/main/OneSection.aspx?section=135.010&bid=6435",
    )
    defined_for = StateCode.MO

    def formula(tax_unit, period, parameters):
        # Eligibility
        # Check for age eligiblity
        age_head = tax_unit("age_head", period)
        age_spouse = tax_unit("age_spouse", period)
        age_threshold = parameters(
            period
        ).gov.states.mo.tax.income.credits.property_tax.age_threshold
        elderly_head = age_head >= age_threshold
        elderly_spouse = age_spouse >= age_threshold
        elderly_head_or_spouse = elderly_head | elderly_spouse

        # Check for disability eligibility
        disabled_head = tax_unit("disabled_head", period)
        disabled_spouse = tax_unit("disabled_spouse", period)
        disabled_head_or_spouse = disabled_head | disabled_spouse

        # Check for military disabled eligibility
        military_disabled_head = tax_unit("military_disabled_head", period)
        military_disabled_spouse = tax_unit("military_disabled_spouse", period)
        military_disabled_head_or_spouse = (
            military_disabled_head | military_disabled_spouse
        )

        # Check for receipt of surviving spouse benefits
        receives_survivor_benefits = (
            add(tax_unit, period, ["social_security_survivors"]) > 0
        )

        return (
            elderly_head_or_spouse
            | disabled_head_or_spouse
            | military_disabled_head_or_spouse
            | receives_survivor_benefits
        )
