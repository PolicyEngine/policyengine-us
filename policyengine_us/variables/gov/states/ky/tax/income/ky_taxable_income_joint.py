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
        agi = person("ky_agi", period)
        standard_deduction = person("ky_standard_deduction_joint", period)
        itemized_deductions = person("ky_itemized_deductions_joint", period)
        # The itemization choice is not dependent on the federal itemization
        deduction = max_(standard_deduction, itemized_deductions)

        return max_(0, agi - deduction)
