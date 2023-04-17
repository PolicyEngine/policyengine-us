from policyengine_us.model_api import *


class oh_personal_exemption(Variable):
    value_type = bool
    entity = TaxUnit
    label = "OH personal exemption"
    defined_for = StateCode.OH
    unit = USD
    definition_period = YEAR
    reference = "https://tax.ohio.gov/static/forms/ohio_individual/individual/2021/pit-it1040-booklet.pdf#page=14"

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        #test for this three
        is_dependent = person("is_tax_unit_dependent", period)#should we create a variable for this in person file? tmr ask nick
        is_tax_unit_head = person("is_tax_unit_head", period) #the variable 'is_tax_unit_head' is defined for 'people', change this to person just for now
        is_spouse = person("is_tax_unit_spouse", period)
        agi = tax_unit("oh_agi", period)
        num_of_dependents = tax_unit.sum(is_dependent)
        personal_exemption_amount = parameters(
            period
        ).gov.states.oh.tax.income.oh_personal_exemption.calc(agi)
        return (
            num_of_dependents + (is_spouse & ~is_dependent) + (is_tax_unit_head & ~is_dependent)
        ) * personal_exemption_amount
