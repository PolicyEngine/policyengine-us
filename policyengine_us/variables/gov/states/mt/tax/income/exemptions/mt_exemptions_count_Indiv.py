from policyengine_us.model_api import *


class mt_exemptions_count_indiv(Variable):
    value_type = int
    entity = Person
    label = "Number of Montana exemptions when married filing separately"
    definition_period = YEAR
    defined_for = StateCode.MT

    def formula(person, period, parameters):
        aged_exemption = person("mt_aged_exemption_indiv", period)
        dependent_exemption = person("mt_dependent_exemption_indiv", period)
        blind = person("is_blind", period)
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        blind_head_or_spouse = (blind & head_or_spouse).astype(int)
        return head_or_spouse * (
            1 + aged_exemption + dependent_exemption + blind_head_or_spouse
        )
