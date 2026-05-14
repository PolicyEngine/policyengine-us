from policyengine_us.model_api import *


class al_ssp(Variable):
    value_type = float
    entity = Person
    label = "Alabama State Supplementary Payment"
    unit = USD
    definition_period = MONTH
    defined_for = "al_ssp_eligible"
    reference = "https://admincode.legislature.state.al.us/api/chapter/660-2-4#page=24"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.al.dhr.ssp
        payment_category = person("al_ssp_payment_category", period)
        return p.amount[payment_category]
