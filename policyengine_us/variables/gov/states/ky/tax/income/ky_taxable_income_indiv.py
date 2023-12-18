from policyengine_us.model_api import *


class ky_taxable_income_indiv(Variable):
    value_type = float
    entity = Person
    label = "Kentucky taxable income when married couples file separately"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.KY
    reference = "https://revenue.ky.gov/Forms/740%20Packet%20Instructions%205-9-23.pdf#page=11"

    def formula(person, period, parameters):
        ky_agi = person("ky_agi_indiv", period)
        standard_deduction = person("ky_standard_deduction_indiv", period)
        itemized_deductions = person("ky_itemized_deductions_indiv", period)
        # Assume that filers itemize if itemized deductions exceed the standard deduction.
        # They do not need to follow their federal itemization choice.
        deduction = max_(standard_deduction, itemized_deductions)

        return max_(0, ky_agi - deduction)
