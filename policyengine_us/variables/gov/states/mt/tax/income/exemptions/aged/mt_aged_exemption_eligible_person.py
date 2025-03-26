from policyengine_us.model_api import *


class mt_aged_exemption_eligible_person(Variable):
    value_type = bool
    entity = Person
    label = "Montana aged exemptions when married couples file separately"
    definition_period = YEAR
    reference = "https://regulations.justia.com/states/montana/department-42/chapter-42-15/subchapter-42-15-4/rule-42-15-402/"
    defined_for = StateCode.MT

    def formula(person, period, parameters):
        p = parameters(period).gov.states.mt.tax.income.exemptions
        age = person("age", period)
        aged = age >= p.age_threshold

        return aged & person("is_tax_unit_head_or_spouse", period)
