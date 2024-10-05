from policyengine_us.model_api import *


class ky_standard_deduction_joint(Variable):
    value_type = float
    entity = Person
    label = "Kentucky standard deduction when married couples file jointly"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.KY

    def formula(person, period, parameters):
        # If filing a joint return, only one standard deduction is allowed
        is_head = person("is_tax_unit_head", period)
        p = parameters(period).gov.states.ky.tax.income.deductions
        return is_head * p.standard
