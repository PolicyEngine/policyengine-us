from policyengine_us.model_api import *


class ky_taxable_income_joint(Variable):
    value_type = float
    entity = Person
    label = "Kentucky taxable income when married couples file jointly"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.KY
    reference = "https://revenue.ky.gov/Forms/740%20Packet%20Instructions%205-9-23.pdf#page=11"

    def formula(person, period, parameters):
        ky_agi = person("ky_agi", period)
        is_head = person("is_tax_unit_head", period)
        total_agi = is_head * person.tax_unit.sum(ky_agi)
        deductions = add(person.tax_unit, period, ["ky_deductions_joint"])

        return max_(0, total_agi - deductions)
