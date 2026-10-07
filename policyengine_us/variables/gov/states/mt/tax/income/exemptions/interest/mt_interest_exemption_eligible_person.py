from policyengine_us.model_api import *


class mt_interest_exemption_eligible_person(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for the Montana interest exemption"
    definition_period = YEAR
    reference = "https://revenuefiles.mt.gov/files/Forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2022_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=25"
    defined_for = StateCode.MT

    def formula(person, period, parameters):
        p = parameters(period).gov.states.mt.tax.income.exemptions

        if p.applies:
            head_or_spouse = person("is_tax_unit_head_or_spouse", period)
            age = person("age", period)
            return person.tax_unit.any(age >= p.interest.age_threshold) & head_or_spouse

        return False
