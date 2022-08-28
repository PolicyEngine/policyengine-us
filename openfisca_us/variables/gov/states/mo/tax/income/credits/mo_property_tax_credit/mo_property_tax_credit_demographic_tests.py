from openfisca_us.model_api import *


class mo_property_tax_credit_demographic_tests(Variable):
    value_type = float
    entity = TaxUnit
    label = "MO property tax credit demographic eligiblity test"
    unit = USD
    definition_period = YEAR
    reference = "https://dor.mo.gov/forms/MO-PTS_2021.pdf"
    defined_for = StateCode.MO

    def formula(tax_unit, period, parameters):
        ##Eligibility
        #vars for age test
        age_head = tax_unit("age_head", period)
        age_spouse = tax_unit("age_spouse", period)
        age_threshold = parameters(period).gov.states.mo.tax.credits.property_tax.age_threshold
        elderly_head = age_head >= age_threshold
        elderly_spouse = age_spouse >= age_threshold
        age_test = elderly_head | elderly_spouse

        #vars for disabled test
        disabled_head = tax_unit("disabled_head", period)
        disabled_spouse = tax_unit("disabled_spouse", period)
        disabled_test = disabled_head | disabled_spouse

        #vars for military disabled test
        military_disabled_head = tax_unit("military_disabled_head", period)
        military_disabled_spouse = tax_unit("military_disabled_spouse", period)
        military_disabled_test = military_disabled_head | military_disabled_spouse

        #vars for surviving spouse benefits test
        #might need to check for only head? not sure how this would work in practice, could more than the head have suvivor benefits in a tax_unit?
        surivor_benefits = tax_unit.members("social_security_survivors", period)
        survivor_benefit_test = surivor_benefits > 0

        return (age_test + disabled_test + military_disabled_test + survivor_benefit_test) >= 1
