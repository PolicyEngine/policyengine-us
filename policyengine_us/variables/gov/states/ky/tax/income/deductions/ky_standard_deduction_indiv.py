from policyengine_us.model_api import *


class ky_standard_deduction_indiv(Variable):
    value_type = float
    entity = Person
    label = "Kentucky standard deduction when married couples file separately"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.KY

    def formula(person, period, parameters):
        return parameters(period).gov.states.ky.tax.income.deductions.standard
