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
        # is_head = person("is_tax_unit_head", period)
        agi = person("ky_agi_joint", period)
        standard_deduction = person("ky_standard_deduction_joint", period)
        itemized_deductions = person("ky_itemized_deductions_joint", period)

        # head_agi = is_head * person.tax_unit.sum(ky_agi)
        # head_standard_deduction = is_head * person.tax_unit.sum(
        #     standard_deduction
        # )
        # head_itemized_deductions = is_head * person.tax_unit.sum(
        #     itemized_deductions
        # )
        # Assume that filers itemize if itemized deductions exceed the standard deduction.
        # They do not need to follow their federal itemization choice.
        deduction = max_(standard_deduction, itemized_deductions)

        return max_(0, agi - deduction)
