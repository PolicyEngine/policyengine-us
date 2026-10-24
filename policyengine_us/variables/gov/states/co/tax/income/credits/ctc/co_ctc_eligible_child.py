from policyengine_us.model_api import *


class co_ctc_eligible_child(Variable):
    value_type = bool
    entity = Person
    label = "Colorado child tax credit eligible child"
    definition_period = YEAR
    reference = (
        "https://leg.colorado.gov/sites/default/files/2023a_1112_signed.pdf#page=4",
        "https://www.law.cornell.edu/uscode/text/26/152#c",
    )
    defined_for = StateCode.CO

    # From 2024, the statute uses IRC 152(c) qualifying-child status,
    # which is retained when the filer can be claimed elsewhere.
    adds = "gov.states.co.tax.income.credits.ctc.eligible_child"
