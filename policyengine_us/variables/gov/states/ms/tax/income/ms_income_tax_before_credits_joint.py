from policyengine_us.model_api import *


class ms_income_tax_before_credits_joint(Variable):
    value_type = float
    entity = Person
    label = "Mississippi income tax before credits when married couples file jointly"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MS

    def formula(person, period, parameters):
        income = person("ms_taxable_income_joint", period)
        rate = parameters(period).gov.states.ms.tax.income.rate
        return rate.calc(income)
