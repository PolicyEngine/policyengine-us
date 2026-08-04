from policyengine_us.model_api import *


class ak_ccap_countable_unearned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Alaska CCAP countable unearned income"
    definition_period = MONTH
    unit = USD
    defined_for = StateCode.AK
    reference = (
        "https://www.akleg.gov/statutesPDF/aac%20Title%207.pdf#page=907",
        "https://health.alaska.gov/media/igiccwuf/child-care-assistance-program-policies-and-procedures.pdf#page=231",
    )

    adds = "gov.states.ak.dpa.ccap.income.countable_income.unearned_sources"
