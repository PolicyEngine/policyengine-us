from policyengine_us.model_api import *


class ky_agi_joint(Variable):
    value_type = float
    entity = Person
    label = "Kentucky adjusted gross income when married couples file jointly"
    unit = USD
    definition_period = YEAR
    reference = "https://revenue.ky.gov/Forms/740%20Packet%20Instructions%205-9-23.pdf#page=11"
    defined_for = StateCode.KY

    def formula(person, period, parameters):
        is_head = person("is_tax_unit_head", period)
        additions = person(
            "ky_additions_joint", period
        )  # Is ky_additions_joint enough?
        agi = person.tax_unit("adjusted_gross_income", period)
        subtractions = person("ky_subtractions_joint", period)  # similarly

        head_agi = is_head * person.tax_unit.sum(agi)
        head_additions = is_head * person.tax_unit.sum(additions)
        head_subtractions = is_head * person.tax_unit.sum(subtractions)

        return is_head * max_(0, head_additions + head_agi - head_subtractions)
