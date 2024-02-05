from policyengine_us.model_api import *


class mt_exemptions_indiv(Variable):
    value_type = float
    entity = Person
    label = "Montana exemptions when married couples file separately"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MT

    def formula(person, period, parameters):
        head_or_spouse = person("is_tax_unit_head_or_spouse", period).astype(int)
        blind = person("is_blind", period)
        blind_head_or_spouse = blind * head_or_spouse
        # Allocate the dependent exemption to the head 
        head = person("is_tax_unit_head", period)
        dependent_exemption = person("mt_dependent_exemptions", period)
        total_dependent_exemption = person.tax_unit.sum(dependent_exemption) * head
        aged_exemption = person("mt_aged_exemption_eligible_person", period).astype(int)
        exemption_count = head_or_spouse + blind_head_or_spouse + total_dependent_exemption + aged_exemption
        p = parameters(period).gov.states.mt.tax.income.exemptions
        return exemption_count * p.amount
