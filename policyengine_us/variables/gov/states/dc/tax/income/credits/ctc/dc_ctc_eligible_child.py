from policyengine_us.model_api import *


class dc_ctc_eligible_child(Variable):
    value_type = bool
    entity = Person
    label = "Whether the child is eligible for the DC CTC"
    definition_period = YEAR
    defined_for = "is_tax_unit_dependent"
    reference = (
        "https://code.dccouncil.gov/us/dc/council/code/sections/47-1806.17"
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.dc.tax.income.credits.ctc.child
        age = person("age", period)
        return age < p.age_threshold
