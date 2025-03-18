from policyengine_us.model_api import *


class ma_tafdc_infant_benefit(Variable):
    value_type = float
    unit = USD
    entity = Person
    label = "Massachusetts Temporary Assistance for Families with Dependent Children (TAFDC) infant benefit"
    definition_period = YEAR
    reference = "https://www.masslegalservices.org/content/75-how-much-will-you-get-each-month"
    defined_for = StateCode.MA

    def formula(person, period, parameters):
        eligible_infant = person("ma_tafdc_eligible_infant", period)
        p = parameters(period).gov.states.ma.dta.tafdc
        return eligible_infant * p.infant_amount
