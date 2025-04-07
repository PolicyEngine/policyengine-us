from policyengine_us.model_api import *


class mo_ptc_taxunit_eligible(Variable):
    value_type = float
    entity = TaxUnit
    label = "Missouri property tax credit taxunit eligible"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://dor.mo.gov/forms/MO-PTS_2021.pdf",
        "https://revisor.mo.gov/main/OneSection.aspx?section=135.010&bid=6435",
    )
    defined_for = StateCode.MO

    def formula(tax_unit, period, parameters):
        # check age
        age_head = tax_unit("age_head", period)
        age_spouse = tax_unit("age_spouse", period)
        p = parameters(period).gov.states.mo.tax.income.credits.property_tax
        elderly_head = age_head >= p.age_threshold
        elderly_spouse = age_spouse >= p.age_threshold
        elderly_head_or_spouse = elderly_head | elderly_spouse
        # check disability
        disabled_head = tax_unit("disabled_head", period)
        disabled_spouse = tax_unit("disabled_spouse", period)
        disabled_head_or_spouse = disabled_head | disabled_spouse
        # check for military disability
        military_disabled_head = tax_unit("military_disabled_head", period)
        military_disabled_spouse = tax_unit("military_disabled_spouse", period)
        military_disabled_head_or_spouse = (
            military_disabled_head | military_disabled_spouse
        )
        # check aged social security survivor benefits eligibility
        survivor_ben = add(tax_unit, period, ["social_security_survivors"]) > 0
        aged_survivor_min_age = p.aged_survivor_min_age
        aged_head = age_head >= aged_survivor_min_age
        aged_spouse = age_spouse >= aged_survivor_min_age
        aged_head_or_spouse = aged_head | aged_spouse
        survivor_benefits_eligible = survivor_ben & aged_head_or_spouse
        return (
            elderly_head_or_spouse
            | disabled_head_or_spouse
            | military_disabled_head_or_spouse
            | survivor_benefits_eligible
        )
