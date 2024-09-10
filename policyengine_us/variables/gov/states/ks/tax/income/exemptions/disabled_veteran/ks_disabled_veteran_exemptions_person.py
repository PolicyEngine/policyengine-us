from policyengine_us.model_api import *


class ks_disabled_veteran_exemptions_person(Variable):
    value_type = float
    entity = Person
    label = "Kansas disabled veteran exemptions for each person"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.KS

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ks.tax.income.exemptions
        disabled = person("is_permanently_and_totally_disabled", period)
        return p.amount * disabled 
    