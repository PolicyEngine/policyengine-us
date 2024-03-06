from policyengine_us.model_api import *


class co_ctc_eligible_child(Variable):
    value_type = bool
    entity = Person
    label = "Colorado child tax credit eligible child"
    definition_period = YEAR
    reference = (
        "https://leg.colorado.gov/sites/default/files/2023a_1112_signed.pdf#page=2",
    )
    defined_for = StateCode.CO

    adds = "gov.states.co.tax.income.credits.ctc.eligible_child"
