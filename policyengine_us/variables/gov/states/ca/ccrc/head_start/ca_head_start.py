from policyengine_us.model_api import *


class ca_head_start(Variable):
    value_type = float
    entity = Person
    label = "Amount of California State Preschool Program (Head Start) benefit"
    definition_period = YEAR
    reference = (
        "https://www.ccrcca.org/headstart/programs/eligibility-requirements/"
    )
    defined_for = StateCode.CA

    def formula(person, period, parameters):
        return person("head_start", period)
