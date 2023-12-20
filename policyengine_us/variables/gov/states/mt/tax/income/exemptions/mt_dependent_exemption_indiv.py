from policyengine_us.model_api import *


class mt_dependent_exemption_indiv(Variable):
    value_type = float
    entity = Person
    label = "Montana dependent exemptions when married couples file separately"
    unit = USD
    definition_period = YEAR
    reference = "https://regulations.justia.com/states/montana/department-42/chapter-42-15/subchapter-42-15-4/rule-42-15-403/"
    defined_for = StateCode.MT

    def formula(person, period, parameters):
        total_dependent_exemptions = person.tax_unit("mt_dependent_exemption_unit", period)
        # Only the head will claim the dependent exemption in the case when a married
        # couple files separately on the same return
        head = person("is_tax_unit_head", period)
        return head * total_dependent_exemptions
