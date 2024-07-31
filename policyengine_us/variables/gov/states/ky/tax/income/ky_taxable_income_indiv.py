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
        ky_agi = person("ky_agi", period)
        deductions = person("ky_deductions_indiv", period)

        return max_(0, ky_agi - deductions)
