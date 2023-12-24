from policyengine_us.model_api import *


class mt_aged_exemption_joint(Variable):
    value_type = int
    entity = Person
    label = "Montana aged exemptions when married filing jointly"
    definition_period = YEAR
    reference = "https://regulations.justia.com/states/montana/department-42/chapter-42-15/subchapter-42-15-4/rule-42-15-402/"
    defined_for = StateCode.MT

    def formula(person, period, parameters):
        aged_exemptions = person.tax_unit.sum("mt_aged_exemption_indiv", period)
        is_head = person("is_tax_unit_head", period)
        return is_head * aged_exemptions
    