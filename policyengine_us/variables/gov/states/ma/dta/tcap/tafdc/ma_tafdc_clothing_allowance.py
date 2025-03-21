from policyengine_us.model_api import *


class ma_tafdc_clothing_allowance(Variable):
    value_type = float
    unit = USD
    entity = Person
    label = "Massachusetts Temporary Assistance for Families with Dependent Children (TAFDC) clothing allowance"
    definition_period = YEAR
    reference = "https://www.masslegalservices.org/content/75-how-much-will-you-get-each-month"
    defined_for = StateCode.MA

    def formula(person, period, parameters):
        eligible_child = person("ma_tafdc_eligible_dependent", period)
        p = parameters(period).gov.states.ma.dta.tcap.tafdc
        return eligible_child * p.clothing_allowance
