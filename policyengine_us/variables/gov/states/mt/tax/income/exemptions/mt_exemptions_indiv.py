from policyengine_us.model_api import *


class mt_exemptions_indiv(Variable):
    value_type = float
    entity = Person
    label = "Montana exemptions when married couples file separately"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MT

    def formula(person, period, parameters):
        exemption_count = person("mt_exemptions_count_indiv", period)
        p = parameters(period).gov.states.mt.tax.income.exemptions
        return exemption_count * p.amount
