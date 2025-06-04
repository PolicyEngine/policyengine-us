from policyengine_us.model_api import *


class base_part_b_premium(Variable):
    value_type = float
    entity = Person
    label = "Medicare Part B Base Premium"
    unit = USD
    documentation = "Medicare Part B Premium."
    definition_period = YEAR
    defined_for = "is_medicare_eligible"

    def formula(person, period, parameters):
        p = parameters(period).gov.hhs.medicare.part_b
        return p.base_premium
 