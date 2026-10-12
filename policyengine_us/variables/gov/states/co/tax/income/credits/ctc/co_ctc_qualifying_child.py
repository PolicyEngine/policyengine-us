from policyengine_us.model_api import *


class co_ctc_qualifying_child(Variable):
    value_type = bool
    entity = Person
    label = "Colorado child tax credit qualifying child"
    definition_period = YEAR
    reference = (
        # C.R.S. 39-22-129(2)(a) and (3.5)(a) - House Bill 23-1112.
        "https://leg.colorado.gov/sites/default/files/2023a_1112_signed.pdf#page=5",
    )
    defined_for = StateCode.CO

    def formula(person, period, parameters):
        age = person("age", period)
        p = parameters(period).gov.states.co.tax.income.credits.ctc
        is_dependent = person("is_tax_unit_dependent", period)
        return is_dependent & (age < p.age_threshold)
