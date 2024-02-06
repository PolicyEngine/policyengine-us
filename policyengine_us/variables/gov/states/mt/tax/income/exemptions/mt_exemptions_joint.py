from policyengine_us.model_api import *


class mt_exemptions_joint(Variable):
    value_type = float
    entity = Person
    label = "Montana exemptions when married couple files jointly"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MT

    def formula(person, period, parameters):
        # Allocate the exemptions to the head
        head = person("is_tax_unit_head", period)
        exemptions = add(person.tax_unit, period, ["mt_exemptions_indiv"])
        p = parameters(period).gov.states.mt.tax.income.exemptions
        return exemptions * head
