from policyengine_us.model_api import *


class id_aabd(Variable):
    value_type = float
    entity = Person
    label = "Idaho AABD cash payment"
    unit = USD
    definition_period = YEAR
    defined_for = "id_aabd_eligible"
    reference = (
        "https://adminrules.idaho.gov/rules/current/16/160305.pdf#page=41",
        "https://www.law.cornell.edu/regulations/idaho/IDAPA-16.03.05.514",
    )

    def formula(person, period, parameters):
        living_arrangement = person("id_aabd_living_arrangement", period)
        p = parameters(period).gov.states.id.dhw.aabd.payment.amount
        monthly_amount = p[living_arrangement]
        return monthly_amount * MONTHS_IN_YEAR
